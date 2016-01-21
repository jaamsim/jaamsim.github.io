bl_info = {
    "name": "JaamSim Mesh Exporter(.jsm)",
    "author": "Matt Chudleigh",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "location": "File > Export > JaamSim Mesh (.jsm)",
    "description": "Export Mesh and Skeletal Data",
    "category": "Import-Export"}

import xml.etree.ElementTree as ET
import os

import bpy

class ExportError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def matrixToString(mat):
    ret = ""
    for i in range(4):
        col = mat.col[i]
        ret += "%f %f %f %f   " % (col.x, col.y, col.z, col.w)
    return ret

def gatherVertexWeights(vert):
    weights = []
    totalWeight = 0 # used to normalize the weights
    # Work out the total weight first for normalization (and the max number per bone)
    for wg in vert.groups:
        totalWeight = totalWeight + wg.weight

    if totalWeight == 0:
        #This vertex is influenced by no bones
        return [(-1, 1)] # The -1 bone is the stationary bone

    # Now build up the output
    for wg in vert.groups:
        weights.append( (wg.group, wg.weight/totalWeight) )

    return weights

def exportGeometry(mesh, geos):
    vertDict = {}
    vertList = []

    indices = []

    mesh.update()
    mesh.update(calc_tessface=True)

    for faceInd in range(len(mesh.tessfaces)):
        face = mesh.tessfaces[faceInd]
        hasUV = len(mesh.tessface_uv_textures) > 0
        if hasUV:
            uv_face = mesh.tessface_uv_textures[0].data[faceInd]
        else:
            uv_face = None

        faceIndices = []
        for vertCount in range(len(face.vertices)):
            # Build up a dictionary (and list) of the vertex, uv, normal combinations
            vertInd = face.vertices[vertCount]

            if face.use_smooth:
                normalVect = mesh.vertices[vertInd].normal
            else:
                normalVect = face.normal

            normal = (normalVect.x, normalVect.y, normalVect.z)

            if hasUV:
                uv = (uv_face.uv_raw[vertCount*2], uv_face.uv_raw[vertCount*2+1])
            else:
                uv = None

            weights = gatherVertexWeights(mesh.vertices[vertInd])

            vertTuple = (vertInd, normal, uv)

            if vertTuple in vertDict:
                dictIndex = vertDict[vertTuple]
            else:
                dictIndex = len(vertDict)
                vertDict[vertTuple] = dictIndex
                vertList.append(vertTuple)

            faceIndices.append(dictIndex)

        if len(face.vertices) == 3:
            # this face is a triangle, just append the face indices
            indices.extend(faceIndices)
        elif len(face.vertices) == 4:
            # this face is a quad, make two triangles out of it
            indices.append(faceIndices[0])
            indices.append(faceIndices[1])
            indices.append(faceIndices[2])

            indices.append(faceIndices[0])
            indices.append(faceIndices[2])
            indices.append(faceIndices[3])

    #We should now have a list of all the vertex, normal, uv pairs, and indices to make triangles, so let's jam this out

    posStr = ""
    norStr = ""
    uvStr = ""
    for vertInd, nor, uv in vertList:
        vertVect = mesh.vertices[vertInd].co

        posStr += "%f %f %f " % (vertVect.x, vertVect.y, vertVect.z)
        norStr += "%f %f %f " % (nor)
        if hasUV:
            uvStr += "%f %f " % uv

    print("Exporting Geometry: " + mesh.name)
    geo = ET.SubElement(geos, "Geometry")
    geo.set('vertices', str(len(vertList)))
    geo.set('ID', mesh.name)

    posNode = ET.SubElement(geo, "Positions")
    posNode.set('dims', '3')
    posNode.text = posStr

    norNode = ET.SubElement(geo, "Normals")
    norNode.set('dims', '3')
    norNode.text = norStr
    if hasUV:
        uvNode = ET.SubElement(geo, "TexCoords")
        uvNode.set('index', '0')
        uvNode.set('dims', '2')
        uvNode.text = uvStr

    maxNumWeights = 0
    for vertInd, _, _ in vertList:
        numWeights = vertVect = len(mesh.vertices[vertInd].groups)
        if numWeights > maxNumWeights:
            maxNumWeights = numWeights

    if maxNumWeights is not 0:
        boneIndexNode = ET.SubElement(geo, "BoneIndices")
        boneIndexNode.set('entriesPerVert', "%d" % maxNumWeights)
        boneWeightsNode = ET.SubElement(geo, "BoneWeights")
        boneWeightsNode.set('entriesPerVert', "%d" % maxNumWeights)
        boneIndexNode.text = ""
        boneWeightsNode.text = ""

        for vertInd, _, _ in vertList:

            weights = gatherVertexWeights(mesh.vertices[vertInd])
            for weightInd in range(maxNumWeights):
                if weightInd < len(weights):
                    index, weight = weights[weightInd]
                else:
                    index, weight = 0, 0
                boneIndexNode.text += ("%d " % index)
                boneWeightsNode.text += ("%f " % weight)


    # And finally the indices
    indexStr = ""
    for i in indices:
      indexStr += "%d " % (i)

    faceNode = ET.SubElement(geo, "Faces")
    faceNode.set('type', 'Triangles')
    faceNode.set('count', "%d" % (len(indices)/3))
    faceNode.text = indexStr

def channelsToVect(chans):
    #Turn these channels into a time and vector tuple
    # start by finding all keyframes times for this channel
    keyTimes = []
    for c in chans:
        for p in c.keyframe_points:
            keyTimes.append(p.co.x)

    keyTimes = sorted(set(keyTimes))
    ret = []
    for time in keyTimes:
        vect = []
        for c in chans:
            vect.append(c.evaluate(time))
        ret.append( (time, vect) )

    return ret

def exportChannels(channels, node, timeOffset, timeScale):
    hasRot = False
    hasLoc = False
    for c in channels:
        if c.data_path.endswith('rotation_quaternion'):
            hasRot = True
        if c.data_path.endswith('location'):
            hasLoc = True

    if hasRot:
        # Export the rotation keys

        #find all 4 channels (w, x, y, z)
        rotChans = [None, None, None, None]
        for c in channels:
            if c.data_path.endswith('rotation_quaternion'):
                rotChans[c.array_index] = c

        # Make sure we have all 4 channels
        for c in rotChans:
            if c is None:
                raise ExportError("Missing rotation channel")

        rotValues = channelsToVect(rotChans)
        rotNode = ET.SubElement(node, 'Rotation')
        tNode = ET.SubElement(rotNode, 'T')
        tNode.text = ""
        wNode = ET.SubElement(rotNode, 'W')
        wNode.text = ""
        xNode = ET.SubElement(rotNode, 'X')
        xNode.text = ""
        yNode = ET.SubElement(rotNode, 'Y')
        yNode.text = ""
        zNode = ET.SubElement(rotNode, 'Z')
        zNode.text = ""
        for t, vect in rotValues:
            tNode.text += "%f " % ( (t*timeScale + timeOffset) / 24) # Scale to the track data, then convert to seconds
            wNode.text += "%f " % vect[0]
            xNode.text += "%f " % vect[1]
            yNode.text += "%f " % vect[2]
            zNode.text += "%f " % vect[3]

    if hasLoc:
        # Export the translation keys

        #find all 3 channels (x, y, z)
        locChans = [None, None, None]
        for c in channels:
            if c.data_path.endswith('location'):
                locChans[c.array_index] = c

        # Make sure we have all 3 channels
        for c in locChans:
            if c is None:
                raise ExportError("Missing location channel")

        locValues = channelsToVect(locChans)
        locNode = ET.SubElement(node, 'Location')
        tNode = ET.SubElement(locNode, 'T')
        tNode.text = ""
        xNode = ET.SubElement(locNode, 'X')
        xNode.text = ""
        yNode = ET.SubElement(locNode, 'Y')
        yNode.text = ""
        zNode = ET.SubElement(locNode, 'Z')
        zNode.text = ""
        for t, vect in locValues:
            tNode.text += "%f " % ( (t*timeScale + timeOffset) / 24) # Scale to the track data, then convert to seconds
            xNode.text += "%f " % vect[0]
            yNode.text += "%f " % vect[1]
            zNode.text += "%f " % vect[2]


def exportAction(track, armNode, mergeGroups):
    if len(track.strips) < 1:
        return # this track is empty

    strip = track.strips[0]
    timeOffset = strip.frame_start - (strip.action_frame_start * strip.scale) # Use the nlatracks timing info (not the actions)
    timeScale = strip.scale
    # TODO: handle more than one strip at a time
    action = strip.action
    actionNode = ET.SubElement(armNode, "Action")
    actionNode.set('name', track.name)
    actionNode.set('length', "%f" % (track.strips[0].frame_end / 24))
    if mergeGroups:
        exportChannels(action.fcurves, actionNode, timeOffset, timeScale)
    else:
        for ag in action.groups:
            groupNode = ET.SubElement(actionNode, "Group")
            groupNode.set('name', ag.name)

            exportChannels(ag.channels, groupNode, timeOffset, timeScale)


def exportArmature(armObj, armsNode):
    arm = armObj.data
    armNode = ET.SubElement(armsNode, "Armature")
    # Find all bones with no parents
    rootBones = list(filter(lambda b: b.parent is None, arm.bones))

    def writeBoneRecursive(bone, node):
        boneNode = ET.SubElement(node, "Bone")
        boneNode.set('name', bone.name)
        boneNode.set('length', ("%f" % bone.length))
        matNode = ET.SubElement(boneNode, "Matrix")
        matNode.text = matrixToString(armObj.matrix_world * bone.matrix_local)

        for child in bone.children:
            writeBoneRecursive(child, boneNode)

    for b in rootBones:
        writeBoneRecursive(b, armNode)

    # Now export the animation tracks associated with this armature
    if armObj.animation_data is not None:
        for track in armObj.animation_data.nla_tracks:
            exportAction(track, armNode, False)

def exportMaterial(matsNode, mat, baseDir):

    matNode = ET.SubElement(matsNode, "Material")
    diffNode = ET.SubElement(matNode, "Diffuse")

    # determine if we use a diffuse texture for this object
    texSlot = mat.texture_slots[mat.active_texture_index]
    hasDiffuseTex = False
    if texSlot is not None:
        tex = texSlot.texture
        if tex.type == 'IMAGE' and texSlot.use_map_color_diffuse:
            # We have an image texture, and it is mapped to diffuse, this should be the one
            hasDiffuseTex = True
            absPath = bpy.path.abspath(tex.image.filepath)
            diffuseImage = os.path.relpath(absPath, baseDir)

    if hasDiffuseTex:
        texNode = ET.SubElement(diffNode, "Texture")
        texNode.set('coordIndex', '0')
        texNode.text = diffuseImage
    else:
        col = ET.SubElement(diffNode, "Color")
        dc = mat.diffuse_color
        col.text = "%f %f %f %f" % (dc.r, dc.g, dc.b, 1)

def export(filename, context):
    obj = context.object

    meshes = []
    meshMap = {}

    arms = []
    armMap = {}

    mats = []
    matMap = {}
    for obj in context.scene.objects:
        # find all meshes and materials and save them to a list (and a map)
        if not isinstance(obj.data, bpy.types.Mesh):
            continue # not a mesh

        mesh = obj.data
        if not mesh.name in meshMap:
            meshMap[mesh.name] = len(meshes)
            meshes.append(mesh)

        mat = obj.active_material
        if not mat.name in matMap:
            matMap[mat.name] = len(mats)
            mats.append(mat)

        arm = obj.find_armature()
        if arm is not None:
            if not arm.name in armMap:
                armMap[arm.name] = len(arms)
                arms.append(arm)

    root = ET.Element("MeshObject")
    geos = ET.SubElement(root, "Geometries")

    for mesh in meshes:
        exportGeometry(mesh, geos)


    matsNode = ET.SubElement(root, "Materials")
    baseDir = os.path.dirname(filename)
    for mat in mats:
        exportMaterial(matsNode, mat, baseDir)


    if len(arms) != 0:
        armsNode = ET.SubElement(root, "Armatures")
        for arm in arms:
            exportArmature(arm, armsNode)

    instancesNode = ET.SubElement(root, "MeshInstances")
    #Now export all mesh instances
    for obj in context.scene.objects:
        if not isinstance(obj.data, bpy.types.Mesh):
            continue # not a mesh

        instNode = ET.SubElement(instancesNode, "MeshInstance")
        meshIndex = meshMap[obj.data.name]
        matIndex = matMap[obj.active_material.name]

        instNode.set("geoIndex", "%d" % meshIndex)
        instNode.set("matIndex", "%d" % matIndex)

        arm = obj.find_armature()
        if arm is not None:
            armIndex = armMap[arm.name]
            instNode.set("armIndex", "%d" % armIndex)

        matrixNode = ET.SubElement(instNode, "Matrix")
        matrixNode.text = matrixToString(obj.matrix_world)

        if len(obj.vertex_groups) != 0:
            boneNameNode = ET.SubElement(instNode, "BoneNames")
            boneNameNode.text = ""
            for vg in obj.vertex_groups:
                boneNameNode.text += vg.name + " "

        if obj.animation_data is not None and len(obj.animation_data.nla_tracks) != 0:
            actionsNode = ET.SubElement(instNode, "Actions")
            for track in obj.animation_data.nla_tracks:
                exportAction(track, actionsNode, True)

    indent(root)
    tree = ET.ElementTree(root)

    tree.write(filename)

    return True

class JaamSimExporter(bpy.types.Operator):
    """Export to the JaamSim mesh file format"""
    bl_idname = "export.jsm"
    bl_label = "Export JaamSim Mesh"

    filepath = bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = ".jsm"

    def execute(self, context):
        success = export(self.filepath, context)

        if success:
            print("Object Successfully exported")
            return {'FINISHED'}
        else:
            print("Export Failed!")
            return {'CANCELLED'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".jsm"
    self.layout.operator(JaamSimExporter.bl_idname, text="JaamSim Mesh (.jsm)").filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
