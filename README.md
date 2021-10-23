# Honeycomb macro
Honeycomb macro for FreeCAD, creates parametric honeycomb feature python object compatible in Part Design.  It can optionally include a border, either elliptical in form or rectangular, offset inwards or outwards.  The object created can be used inside a Part Design body or outside of Part Design.

<img src="honeycomb_scr1.png" alt="screenshot1 showing elliptical border"><br/>
<br/>
<img src="honeycomb_scr2.png" alt="screeenshot2 showing rectangular border"><br/>

## Toolbar Icon
<img src="Honeycomb.svg"> <a href="Honeycomb.svg">Download</a> the toolbar Icon.<br/>

## Installation
Not yet available in the addon manager.  Place the Honeycomb.FCMacro file into your macro folder.  On first run it offers to create another file: honeycomb.py.  The .py file is needed in order for the Honeycomb objects to be parametric after restarting FreeCAD and opening a document containing one of the objects.

## Usage
Run the macro to create the Honeycomb object with default settings.  If there is an active Part Design Body in the document it places itself into the Body.  Otherwise it is placed in the document, but not in the Body.  You can drag/drop into the Body if you want to use it in that manner.













#### Changelog
##### 0.2021.10.22.rev2
Ensure on deletion the next feature in the Part Design body has its BaseFeature correctly reassigned to the object now in front of it.
##### 0.2021.10.22
Initial upload
