*********************************************************************
* FILES NECESSARY                                                   *
*********************************************************************

The two files needed to convert DWG files to OpenCOLLADA files are:

 convertDWGtoDAE.ms
 convertDWGtoDAE.bat

*********************************************************************
* INSTRUCTIONS                                                      *
********************************************************************* 
 
Place the two files above in the same folder as the .dwg files you wish to convert, and then run the .bat file. 

Leave the computer alone if possible (see GENERAL NOTES).

The rest will take care of itself.
 
*********************************************************************
* GENERAL NOTES                                                     *
*********************************************************************

The script only takes a .dwg file and exports it into OpenCOLLADA through 3dsMAX. If there are custom objects(e.g. AutoPLANT) that are not supported in
3dsMAX, these must either be dealt with manually prior to converting, or you can live with them not showing up.

While this currently only converts .dwg to .DAE, a couple quick edits to the .ms file can customize this script to any import/export combination supported
by 3dsMAX.
 
There are a couple assumptions regarding where things live:

1. The 3dsMax executable lives at "C:\Program Files\Autodesk\3ds Max Design 2012" - if it does not that will need to be adjusted in the .bat file.

2. The user is operating on Windows 7 or 8 so that the ini file for dwg import can be manipulated to control import settings. 
   The main use of this is to select a correct import option to get colours right by accessing a .ini file.
   
Regarding leaving the computer alone, this is because Maxscript can occasionally have difficulty with obtaining the window handle. In fact,
it will sometimes grab the handle for a non-3dsmax window, and 'press the default button' (the 'Enter' key). This obviously won't have impact on
the conversion, so if you need to still use your computer while converting, keep in mind you may need to click through a few dialogue pop-ups.

Also, the equivalent of interacting with the dialogue box for import options through Maxscript, to the best I could tell, was to create and set whatever parameters
desired through a .ini file. Doing this makes some assumptions about the version of Maxscript, OS, etc., but it's straightforward to change the pertinent line to whatever
the destination actually is (iniFileLocation).