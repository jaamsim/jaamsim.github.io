-- ************************************************************************************
-- * JaamSim Discrete Event Simulation                                                *
-- * Copyright (C) 2014 Ausenco Engineering Canada Inc.                               *
-- *                                                                                  *
-- * This program is free software: you can redistribute it and/or modify             *
-- * it under the terms of the GNU General Public License as published by             *
-- * the Free Software Foundation, either version 3 of the License, or                *
-- * (at your option) any later version.                                              *
-- *                                                                                  *
-- * This program is distributed in the hope that it will be useful,                  *
-- * but WITHOUT ANY WARRANTY; without even the implied warranty of                   *
-- * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    *
-- * GNU General Public License for more details.                                     *
-- ************************************************************************************



--This is a callback function that handles .DWG files with no convertable objects.
--When this window appears, it presses the default button (which is usually 'OK')
--However, MaxScript has a fun feature where it can sometimes get the window handle
--of the current window, **even if not a 3dsmax window**, and will press the default 
--button, which is Enter. So when running the script, it is best to leave the computer
--running it fully alone.
fn checkDialog = (
 local hwnd = dialogMonitorOps.getWindowHandle()
 uiAccessor.PressDefaultButton() hwnd
 return true
)
 
--this sets up the monitor for when a dialogue box pops up, and goes
--to the checkDialog callback function.
dialogMonitorOps.interactive = false
dialogMonitorOps.unregisterNotification ID:#test
dialogMonitorOps.registerNotification checkDialog ID:#test 
dialogMonitorOps.enabled = true


--this line REQUIRES that this script be called from its corresponding
--batch file, otherwise the currentdir function can be unreliable 
dir = sysInfo.currentdir
 
if dir != undefined then
(
    --here all the files with the appropriate extension (.dwg) are grabbed
    files = getFiles (dir + @"\*.dwg")

	--the dwg_dxf_import.ini file contains options corresponding to the Import Options menu in 3dsMAX.
	--the biggest things we want to set here is the CombineScenarioID, which sets the import option to 'Layer, Blocks as Node Hierarchy'
	--which in short means 'get the colours right.' The rest of the settings that normally appear in the file have 
	--been included to be explicit.	
    iniFileLocation = @"C:\Users\" + sysInfo.username + @"\AppData\Local\Autodesk\3dsMaxDesign\2012 - 64bit\enu\plugcfg\dwg_dxf_import.ini"

    setINISetting   iniFileLocation "LastUsedSettings"  "SmoothAngle" "31.0"
    setINISetting   iniFileLocation "LastUsedSettings"  "DWG_ReplaceSceneMtlDefs" "ON"
    setINISetting   iniFileLocation "LastUsedSettings"  "DWG_ACISDeviation" "5.000000"
    setINISetting   iniFileLocation "LastusedSettings"  "CombineScenarioID" "20"
    setINISetting   iniFileLocation "LastusedSettings"  "TranslateMaterials" "OFF"
    setINISetting   iniFileLocation "LastusedSettings"  "AssignMaterials" "OFF"		
    setINISetting	iniFileLocation	"LastUsedSettings"	"CapClosedEntities"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"AutoSmooth"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"UnifyNormals"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"Weld"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"ShapeSteps"	"10"
    setINISetting	iniFileLocation	"LastUsedSettings"	"FullReload"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"ReloadSelected"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"AddOriginHelper"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"ConvertUnits"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"AssigningLayers"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"AutoEdge"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"CombineFlags"	"7"
    setINISetting	iniFileLocation	"LastUsedSettings"	"GiveNewNodesUniqueNames"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"ReassignLayersOnReload"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"WeldThreshold"	"0.1"
    setINISetting	iniFileLocation	"LastUsedSettings"	"ClosePolysThreshhold"	"0.001"
    setINISetting	iniFileLocation	"LastUsedSettings"	"MinLineLength"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"MeshVertexTolerance"	"0.001"
    setINISetting	iniFileLocation	"LastUsedSettings"	"AutoEdgeDegrees"	"5"
    setINISetting	iniFileLocation	"LastUsedSettings"	"BoundingBoxSizeLimit"	"1000000"
    setINISetting	iniFileLocation	"LastUsedSettings"	"BoundingBoxCenterDistanceLimit"	"1000000"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_ResetThickness"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_ResolveXrefs"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_ReResolveAllXrefs"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_LayerNameBasis"	"4"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_NeverUnifyACISNormals"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslateLights"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslateGrids"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslateFrozenLayers"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslateHatches"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslatePoints"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslateCameras"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_ExtrudeWithModifier"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_ReplaceSceneMtlAssignments"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_UVWGeneration"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_TranslateSunAndSky"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_AdtObjectTranslation"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Thickness"	"1"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Sides"	"12"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Angle"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_ViewportThickness"	"1"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_ViewportSides"	"12"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_ViewportAngle"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Renderable"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_GenUVs"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_DispRenderMesh"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_UseViewport"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_ViewportOrRenderer"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_UsePhysicalScaleUVs"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Rectangular"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Width"	"2"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Length"	"6"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Angle2"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_AspectLock"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_VptRectangular"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_VptWidth"	"2"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_VptLength"	"6"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_VptAngle2"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_VptAspectLock"	"OFF"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Autosmooth"	"ON"
    setINISetting	iniFileLocation	"LastUsedSettings"	"DWG_Shape_Threshold"	"0.698132"
    setINISetting	iniFileLocation	"LastUsedSettings"	"SystemUnitTypeWhenSaved"	"0"
    setINISetting	iniFileLocation	"LastUsedSettings"	"SystemUnitScaleWhenSaved"	"1"	
    setINISetting   iniFileLocation	"LastUsedSettings"	"DWG_TranslateMaterials"	"OFF"
    setINISetting   iniFileLocation	"LastUsedSettings"	"DWG_AssignMaterials"	"OFF"
	
    --takes all the files of the extension of interest, and exports them into OpenCOLLADA (using:OpenCOLLADAExporter)
    for f in files do 
    (
        resetMaxFile #noPrompt
        importFile f #noPrompt
	    exportFile (dir +@"\" + (getFilenameFile f) + @".DAE") #noPrompt using:OpenCOLLADAExporter
    )
)

dialogMonitorOps.unregisterNotification ID:#test
dialogMonitorOps.enabled = false

quitMax #noPrompt