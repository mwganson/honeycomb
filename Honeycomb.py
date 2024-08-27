# -*- coding: utf-8 -*-
__version__ = "0.2024.08.27"

#Honeycomb macro -- creates a feature python parametric honeycomb object for Part Design workbench
#2021, by <TheMarkster> LGPL2.1 or later
import FreeCAD, FreeCADGui, Part
class Honeycomb:
    def __init__(self,obj):
        obj.addExtension("Part::AttachExtensionPython")
        obj.addProperty("App::PropertyFloat","Radius","Honeycomb","Circumradius of the hexagons").Radius = 1
        obj.addProperty("App::PropertyFloat","Separation","Honeycomb","Separation between hexagons").Separation = .5
        obj.addProperty("App::PropertyFloat","Length","Honeycomb","Length of grid").Length = 10
        obj.addProperty("App::PropertyFloat","Width","Honeycomb", "Width of grid").Width = 15
        obj.addProperty("App::PropertyFloat","Height","Honeycomb","Height of grid").Height = 3
        obj.addProperty("App::PropertyBool","EllipticalGrid","Honeycomb","If True, make an elliptical grid of minor diameter = Width, Major Diameter = Length").EllipticalGrid = True
        obj.addProperty("App::PropertyFloatConstraint","XAdjust","Honeycomb","Adjust hexagons in the X direction").XAdjust = (0,-10e4,10e4,.1)
        obj.addProperty("App::PropertyFloatConstraint","YAdjust","Honeycomb","Adjust hexagons in the Y direction").YAdjust = (0,-10e4,10e4,.1)
        obj.addProperty("App::PropertyFloat","BorderOffset","Honeycomb","Offset for border (0 = no border) -1 for inward offset").BorderOffset = 1
        obj.addProperty("App::PropertyFloatConstraint","BorderHeightOffset","Honeycomb","Height Offset for border (0 = same as Height)").BorderHeightOffset = (0.1,-10e4,10e4,.1)
        obj.addProperty("App::PropertyLink","Profile","Honeycomb","Profile, e.g. sketch, to use in place of hexagon, should have radius = 1, centered on origin")
        obj.addProperty("App::PropertyInteger","CountXAdjust","Honeycomb","default: 0 -- amount to add to number of hexagons on X axis")
        obj.addProperty("App::PropertyInteger","CountYAdjust","Honeycomb","default: 0 -- amount to add to number of hexagons on Y axis")
        obj.addProperty("App::PropertyString","Version","Honeycomb","Version of macro this object was created with").Version = __version__
        obj.addProperty("App::PropertyBool","SquareGrid","Honeycomb","If true, make a square grid instead of hexagon grid").SquareGrid = False
        obj.setEditorMode("Placement",0)
        obj.Proxy = self
        self.fpName = obj.Name

    def makeHexagon(self,radius,origin):
        '''makes a hexagon based on radius and origin, returns it as a wire
        unless a profile is linked to Profile property'''
        fp = FreeCAD.ActiveDocument.getObject(self.fpName)
        if hasattr(fp,"Profile") and fp.Profile:
            profile = fp.Profile
            if not hasattr(profile,"Shape"):
                raise Exception("Invalid profile\n")
            shp = profile.Shape.copy()
            shp.Placement.move(origin)
            shp.scale(radius,origin)
            return shp
        else:
            sin60 = 0.8660254037844386
            tups = [(-1,0,0),(-.5,sin60,0),(.5,sin60,0),(1,0,0),(.5,-sin60,0),(-.5,-sin60,0),(-1,0,0)]
            pts = [FreeCAD.Vector(tup).add(origin) for tup in tups]
            poly = Part.makePolygon(pts).scale(radius,origin)
            return poly


    def makeCross(self,radius,origin):
        '''makes cross based on radius and origin, returns it as a wire
        unless a profile is linked to Profile property'''
        fp = FreeCAD.ActiveDocument.getObject(self.fpName)
        if hasattr(fp,"Profile") and fp.Profile:
            profile = fp.Profile
            if not hasattr(profile,"Shape"):
                raise Exception("Invalid profile\n")
            shp = profile.Shape.copy()
            shp.Placement.move(origin)
            shp.scale(radius,origin)
            face = Part.makeFace(shp,"Part::FaceMakerBullseye")
            return face
        else:
            tups = [(-1,-1,0),(1,-1,0),(1,1,0),(1,1,0),(-1,1,0),(-1,-1,0)]
            pts = [FreeCAD.Vector(tup).add(origin) for tup in tups]
            poly = Part.makePolygon(pts).scale(radius,origin)
            face = Part.makeFace(poly, "Part::FaceMakerBullseye")
            #Part.show(face,'face"')
            return face

    def makeCrossGrid(self, fp):
        #face = self.makeCross(1, FreeCAD.Vector(0,0,0))

        yInt = (2 * fp.Radius+fp.Separation)
        xInt = (2 * fp.Radius+fp.Separation)
        firstX = 0
        firstY = 0
        countX = round(fp.Width/xInt) + 1
        countY = round(fp.Length/yInt) + 1
        if hasattr(fp,"CountXAdjust"):
            countX += fp.CountXAdjust
            countY += fp.CountYAdjust
        vectors = []
        for xx in range(-1,int(countX)):
            for yy in range(-1,int(countY)):
                vectors.append(FreeCAD.Vector(firstX + xx * xInt, firstY + yy * yInt, 0)+FreeCAD.Vector(fp.XAdjust,fp.YAdjust,0))
        array = [self.makeCross(fp.Radius, v) for v in vectors]
        #crosses = Part.makeCompound(array)
        crosses = Part.makeCompound(array)

        cross_faces = crosses.extrude(FreeCAD.Vector(0,0,1)).removeSplitter()
        #cross_faces = Part.makeFace(crosses,"Part::FaceMakerCheese")
       # rect = Part.makePolygon()
        #Part.show(cross_faces, "cross_faces")
        solid = self.handleElliptical(fp, cross_faces)
        return solid



    def makeHoneycomb(self,fp):
        tan15 = 0.2679491924311227
        sin60 = 0.8660254037844386
        yInt = (2 * fp.Radius + fp.Separation - tan15 * fp.Radius)
        xInt = (2 * sin60 * (fp.Radius * 2 + fp.Separation - tan15 * fp.Radius))
        array2XPos = (sin60 * (fp.Radius * 2 + fp.Separation - tan15 * fp.Radius))
        array2YPos = yInt / 2.0
        firstX = fp.Radius
        firstY = fp.Radius
        countX = round(fp.Width/xInt) + 1
        countY = round(fp.Length/yInt) + 1
        if hasattr(fp,"CountXAdjust"):
            countX += fp.CountXAdjust
            countY += fp.CountYAdjust
        vectors = []
        for xx in range(-1,int(countX)):
            for yy in range(-1,int(countY)):
                vectors.append(FreeCAD.Vector(firstX + xx * xInt, firstY + yy * yInt, 0)+FreeCAD.Vector(fp.XAdjust,fp.YAdjust,0))
        array = [self.makeHexagon(fp.Radius, v) for v in vectors]
        array.extend([self.makeHexagon(fp.Radius, v  + FreeCAD.Vector(array2XPos,array2YPos,0)) for v in vectors[:-int(countY+1)]])
        hexagons = Part.makeCompound(array)
        hex_faces = Part.makeFace(hexagons,"Part::FaceMakerCheese")
        solid = self.handleElliptical(fp, hex_faces)
        return solid


    def handleElliptical(self, fp, hex_faces):
        if not fp.EllipticalGrid:
            rectTups = [(0,0,0),(fp.Width,0,0),(fp.Width,fp.Length,0),(0,fp.Length,0),(0,0,0)]
            rect_pts = [FreeCAD.Vector(tup) + FreeCAD.Vector(-fp.Radius,0,0) for tup in rectTups]
            rect = Part.makePolygon(rect_pts)
            rect_face = Part.makeFace(rect,"Part::FaceMakerCheese")
            cut = rect_face.cut(hex_faces)
            cut.translate(-cut.BoundBox.Center)
            if hasattr(cut,"Face1"):
                normal = cut.Face1.normalAt(0,0).normalize()
            else:
                normal = FreeCAD.Vector(0,0,1)
            cut = cut.extrude(normal * fp.Height)
            if fp.BorderOffset == 0:
                return cut
            else:
                border = rect_face.makeOffset2D(fp.BorderOffset, join=2, fill=True)
                border.translate(-border.BoundBox.Center)
                border = border.extrude(border.Face1.normalAt(0,0).normalize()*(fp.Height + fp.BorderHeightOffset))
                fuse = border.fuse(cut)
                return fuse
        else:
            if fp.Width >= fp.Length:
                ellipse = Part.Ellipse(FreeCAD.Vector(0,0,0),fp.Width/2,fp.Length/2).toShape()
            else:
                ellipse = Part.Ellipse(FreeCAD.Vector(0,0,0),fp.Length/2,fp.Width/2)
                plm = FreeCAD.Placement()
                plm.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0,0,1),90)
                ellipse.rotate(plm)
                ellipse = ellipse.toShape()
            ellipse_face = Part.makeFace(ellipse,"Part::FaceMakerCheese")
            hex_faces.translate(ellipse_face.BoundBox.Center - hex_faces.BoundBox.Center + FreeCAD.Vector(fp.XAdjust, fp.YAdjust, 0))
            cut = ellipse_face.cut(hex_faces)
            if hasattr(cut,"Face1"):
                normal = cut.Face1.normalAt(0,0).normalize()
            else:
                normal = FreeCAD.Vector(0,0,1)
            cut = cut.extrude(normal * fp.Height)
            if fp.BorderOffset == 0:
                return cut
            else:
                if fp.Width >= fp.Length:
                    ellipse_offset = Part.Ellipse(FreeCAD.Vector(0,0,0),fp.Width / 2 + fp.BorderOffset, fp.Length / 2 + fp.BorderOffset).toShape()
                else:
                    ellipse_offset = Part.Ellipse(FreeCAD.Vector(0,0,0),fp.Length / 2 + fp.BorderOffset, fp.Width / 2 + fp.BorderOffset)
                    ellipse_offset.rotate(plm)
                    ellipse_offset = ellipse_offset.toShape()
                ellipse_offset_face = Part.makeFace(ellipse_offset,"Part::FaceMakerCheese")
                if fp.BorderOffset > 0:
                    border = ellipse_offset_face.cut(ellipse_face)
                else:
                    border = ellipse_face.cut(ellipse_offset_face)
                border = border.extrude(border.Face1.normalAt(0,0).normalize()*(fp.Height + fp.BorderHeightOffset))
                fuse = border.fuse(cut)
                return fuse

    def execute(self,fp):
        if not hasattr(fp, "SquareGrid"):
            fp.addProperty("App::PropertyBool","SquareGrid","Honeycomb","Whether to make honeycomb grid or square grid").SquareGrid = False
        shape = self.makeHoneycomb(fp) if not fp.SquareGrid else self.makeCrossGrid(fp)
        fp.positionBySupport()
        shape.Placement = fp.Placement

       #shape.transformShape(fp.Placement.inverse().toMatrix(), True)
        if hasattr(fp,"AddSubShape"):
            fp.AddSubShape = shape
        if hasattr(fp,"BaseFeature") and fp.BaseFeature:
            full_shape = shape.fuse(fp.BaseFeature.Shape)
            full_shape.transformShape(fp.Placement.inverse().toMatrix(),True)
            fp.Shape = full_shape
        else:
            fp.Shape = shape


class HoneycombVP:

    def __init__(self, obj):
        '''Set this object to the proxy object of the actual view provider'''
        obj.Proxy = self

    def attach(self, obj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = obj.Object

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        # fp is the handled feature, prop is the name of the property that has changed
        pass

    def getDisplayModes(self,obj):
        '''Return a list of display modes.'''
        modes=[]
        modes.append("Flat Lines")
        return modes

    def getDefaultDisplayMode(self):
        '''Return the name of the default display mode. It must be defined in getDisplayModes.'''
        return "Flat Lines"

    def setDisplayMode(self,mode):
        '''Map the display mode defined in attach with those defined in getDisplayModes.\
           Since they have the same names nothing needs to be done. This method is optional'''
        return mode

    def onChanged(self, vp, prop):
        '''Here we can do something when a single property got changed'''
        #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + ""+chr(10))

    def claimChildren(self):
        return []

    def setupContextMenu(self, vobj, menu):
        pass

    def setEdit(self,vp,modNum):
        pass

    def onDelete(self, vobj, subelements):
        if hasattr(vobj.Object,"_Body") and vobj.Object._Body: #do this only when the object is in a PD body
            #need to ensure the next feature in the tree's BaseFeature property points to our BaseFeature
            solids = [feat for feat in vobj.Object._Body.Group if feat.isDerivedFrom("PartDesign::Feature") and feat.BaseFeature == vobj.Object]
            if len(solids) == 1: #found previous solid feature
                solids[0].BaseFeature = vobj.Object.BaseFeature
        return True

    def getIcon(self):
        '''Return the icon in XPM format which will appear in the tree view. This method is\
               optional and if not defined a default icon is shown.'''
        XPM = '''
/* XPM */
static char *_634945598709[] = {
/* columns rows colors chars-per-pixel */
"64 64 223 2 ",
"   c #03F603F602CA",
".  c #099C099C0429",
"X  c #042F042F0A0A",
"o  c #0AD20AD20B7D",
"O  c #11DE11DE0269",
"+  c #1A191A190606",
"@  c #13E913E90C8D",
"#  c #1BF71BF70A78",
"$  c #0375037513DB",
"%  c #08C908C91212",
"&  c #038403841D1C",
"*  c #14D514D51394",
"=  c #1CDC1CDC1252",
"-  c #147B147B1D50",
";  c #19B619B61927",
":  c #23F923F9042F",
">  c #2B6B2B6B03E4",
",  c #20A020A00D0D",
"<  c #3400340004D2",
"1  c #3B6E3B6E09A3",
"2  c #22BC22BC1CEA",
"3  c #292929291A9B",
"4  c #378D378D1A70",
"5  c #0429042922C6",
"6  c #0C4C0C4C2464",
"7  c #080808082928",
"8  c #1B1B1B1B2444",
"9  c #177717772848",
"0  c #20E120E12222",
"q  c #2626262627A7",
"w  c #2BB72BB72BA0",
"e  c #3131313123A4",
"r  c #3A3A3A3A2379",
"t  c #23E423E43252",
"y  c #2B2B2B2B33C1",
"u  c #390539053467",
"i  c #33B433B43B7B",
"p  c #390E390E3A3A",
"a  c #482848280666",
"s  c #56225622056C",
"d  c #5F095F090B0B",
"f  c #4747474719C4",
"g  c #5CF65CF6167D",
"h  c #537853781DD5",
"j  c #6BEB6BEB02C3",
"k  c #674267420909",
"l  c #76767676095F",
"z  c #69D769D71482",
"x  c #65A565A51DDE",
"c  c #753475341C9D",
"v  c #78AB78AB1DB7",
"b  c #535253522020",
"n  c #459A459A3CE7",
"m  c #1D1D1D1D4202",
"M  c #297F297F4BF6",
"N  c #3B3B3B3B403F",
"B  c #262626265757",
"V  c #3737373757D7",
"C  c #448444844444",
"Z  c #464646464948",
"A  c #515151514F4F",
"S  c #54A954A951A7",
"D  c #61E261E25D5D",
"F  c #4CCD4CCD6464",
"G  c #5DDE5DDE7373",
"H  c #640E640E62B8",
"J  c #606060606A6A",
"K  c #717171716C6C",
"L  c #68A868A87939",
"P  c #797979797676",
"I  c #7DFD7DFD7BBB",
"U  c #858585850AB5",
"Y  c #890989090848",
"T  c #98179817065C",
"R  c #9A199A190B4B",
"E  c #85858585114C",
"W  c #8585858519B3",
"Q  c #8A8A8A8A1798",
"!  c #919091901111",
"~  c #929292921980",
"^  c #A34DA34D0909",
"/  c #AE0DAE0D0C2C",
"(  c #B6B5B6B50157",
")  c #B413B4130D8E",
"_  c #BC28BC280B54",
"`  c #A3A2A3A210DE",
"'  c #AC11AC111178",
"]  c #B80DB80D1515",
"[  c #BA79BA792727",
"{  c #BFBFBFBF3838",
"}  c #C3C3C3C30505",
"|  c #CE4DCE4D0182",
" . c #C4B3C4B30AAB",
".. c #CBFECBFE0A71",
"X. c #D4BFD4BF0317",
"o. c #DCF6DCF603E9",
"O. c #D5D5D5D50BE1",
"+. c #DC14DC1409D1",
"@. c #C419C4191212",
"#. c #CE4DCE4D1515",
"$. c #C9C9C9C91B9C",
"%. c #DBDBDBDB1495",
"&. c #E4D0E4D003A1",
"*. c #EC35EC350303",
"=. c #E387E3870A0A",
"-. c #ED97ED9709ED",
";. c #F54BF54B0317",
":. c #FE79FE790364",
">. c #F3DDF3DD0873",
",. c #FF69FF690934",
"<. c #E2E2E2E21293",
"1. c #E539E53919C4",
"2. c #F3F2F3F21616",
"3. c #F474F4741BDC",
"4. c #C645C6452626",
"5. c #DD87DD87234E",
"6. c #DFDEDFDE2E2E",
"7. c #C9C8C9C83535",
"8. c #C706C70638F9",
"9. c #D8D7D8D735E0",
"0. c #E423E4232666",
"q. c #F453F45323B4",
"w. c #F5F5F5F52C2C",
"e. c #EC96EC963636",
"r. c #F5F5F5F53ABB",
"t. c #8B8B8B8B4A4A",
"y. c #BA39BA394606",
"u. c #BBBBBBBB56AC",
"i. c #8A0A8A0A77F8",
"p. c #969696967171",
"a. c #AFAFAFAF71F2",
"s. c #BABABABA7434",
"d. c #CBCACBCA4949",
"f. c #D983D9834CA2",
"g. c #CB4BCB4B5454",
"h. c #DB5BDB5B5252",
"j. c #F84CF84C4FFA",
"k. c #C747C7476A6A",
"l. c #D555D55569EA",
"z. c #D514D5146BAB",
"x. c #C646C64675B5",
"c. c #CDCDCDCD7979",
"v. c #D353D3537575",
"b. c #DD53DD537E92",
"n. c #E2E2E2E26C6C",
"m. c #E565E5657E7E",
"M. c #585858589919",
"N. c #787878788606",
"B. c #777777779191",
"V. c #7B7B7B7BB737",
"C. c #89DF89DF84DA",
"Z. c #8AF18AF18AF1",
"A. c #922092208D70",
"S. c #88328832953F",
"D. c #952795279502",
"F. c #999999999C46",
"G. c #B8B8B8B88B8B",
"H. c #A1A1A1A198EE",
"J. c #BABABABA9898",
"K. c #8FE58FE5A7FD",
"L. c #A3A3A3A3A2CD",
"P. c #A7A7A7A7A8A8",
"I. c #ADE0ADE0ABAB",
"U. c #B272B272AF6F",
"Y. c #BBBBBBBBAAAA",
"T. c #A8A8A8A8B60B",
"R. c #B6F6B6F6B620",
"E. c #BCBCBCBCB986",
"W. c #CC0BCC0B8383",
"Q. c #C706C7068949",
"!. c #DB30DB3087B2",
"~. c #C9C9C9C99999",
"^. c #D7D7D7D796EC",
"/. c #DC0EDC0E9595",
"(. c #E83DE83D8BE1",
"). c #E1E1E1E19696",
"_. c #C6C6C6C6A650",
"`. c #DCDCDCDCA0A0",
"'. c #CBF6CBF6B1B1",
"]. c #C35CC35CB8EB",
"[. c #E928E928A8A8",
"{. c #EEEEEEEEBBBB",
"}. c #94949494C6C6",
"|. c #ADADADADC8C8",
" X c #BD12BD12C6C6",
".X c #BDBDBDBDD353",
"XX c #AFAFAFAFFCFC",
"oX c #B8B8B8B8FCFC",
"OX c #C5C5C5C5C444",
"+X c #CB5DCB5DC355",
"@X c #C2C2C2C2CA74",
"#X c #CDF2CDF2CC83",
"$X c #DBDBDBDBC5C5",
"%X c #DD76DD76C5F8",
"&X c #C848C848D655",
"*X c #D4F9D4F9D3D3",
"=X c #D8D8D8D8D6D6",
"-X c #D3D3D3D3DB5B",
";X c #DBFBDBFBDD1C",
":X c #E464E464CACA",
">X c #F4F4F4F4C4C4",
",X c #EEEEEEEED353",
"<X c #E73CE73CD8D8",
"1X c #E4A4E4A4DD9D",
"2X c #C646C646E666",
"3X c #D959D959E767",
"4X c #CDCDCDCDF3F3",
"5X c #C29DC29DFCC5",
"6X c #D871D871F82A",
"7X c #DC5CDC5CFD52",
"8X c #E5E5E5E5E476",
"9X c #E5E5E5E5EAEA",
"0X c #EBCEEBCEECCF",
"qX c #F1F1F1F1E464",
"wX c #F4C9F4C9ECEC",
"eX c #E6E6E6E6F5F5",
"rX c #ED0CED0CF6B6",
"tX c #E564E564FD49",
"yX c #EC9CEC9CFE0D",
"uX c #F30FF30FF348",
"iX c #FAA4FAA4F5CA",
"pX c #F624F624FE14",
"aX c None",
/* pixels */
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXpXyX6X7X7X7XyXpXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXpX3X%X/.b.b.m.m.b.b.b.m.m.m.b.b.`.$X7XpXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXtX%X!.(.!.f.%.o.o.&.>.,.:.,.,.>.&.o.o.5.f.v.(.!.:XtXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXpX=X)./.f.X.*.,.,.,.,.,.,.,.,.,.,.,.,.,.,.:.:.,.,.*.X.f./.).1XiXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXpX:X[.l.X.:.:.:.:.,.,.-.=.) ) ` ` ` ` ` ' ) ) =.-.,.,.,.:.,.,.| l.[.:XpXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaX1X[.d.&.,.:.,.:.=. ./ / R ..f 2 6 & & & 5 & 2 e ..) / /  .-.,.,.:.,.&.g.[.8XaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXpX{.k.*.:.,.,.-. ._ E 4 & t o >.' Z C C C C C C C x ,.d q & 4 Y ) ..;.,.,.:.&.x.{.pXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXwX$X| :.,.,.-...^ ; 6 w p u C.V T :.>X,X,X,X,X,X,X>X:. .w C.u p w 6 0 / ..-.,.,.,.| $XrXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXqXJ.;.,.,.>.O.! 5 ; w D #XaXaXaXiX- ;.*.8.7.7.7.7.8.X.:.X #XaXaXaX+XS w ; 5 R O.,.,.:.>.~.qXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXwXu.:.,.,.;.) 5 = 2 I.aXaXaXaXaXaXaXV.} *.o.&.o.o.o.o.&.:.B pXaXaXaXaXaXiXL.0 ; 5 _ >.,.,.:.u.qXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXiXy.:.,.,.*.@.E 6 #XpXaXaXaXaXaXaXaXaX(.:.f 7 7 7 7 7 7 & ,.j.aXaXaXaXaXaXaXaXaX].* 0 _ *.,.,.:.y.iXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXpXa.:.,.,.:.& ) :.iXaXaXaXaXaXaXaXaXaX6X:.,.  n p u u u n    .:.2XaXaXaXaXaXaXaXaXaXiX:.:.& :.,.,.:.a.aXaXaXaXaXaXaXaX",
"aXaXaXaXaX&X:.,.,.,.$ X   :.o.aXaXaXaXaXaXaXaXaX_ :.  0XaXiXaXaXaXaXiX  :.| aXaXaXaXaXaXaXaXaX] :.    $ :.,.,.:..XaXaXaXaXaXaXaX",
"aXaXaXaXpX&.,.,.:.o X uXS.a :.a.aXaXaXaXaXaXaX.X:./ 7 aXaXaXaXaXaXaXaXG j :.J.aXaXaXaXaXaXaX&X:._ 5 iX% % :.,.,.=.pXaXaXaXaXaXaX",
"aXaXaXaXu.:.,.,., $ 9XaXuX  ,.,.XX5X5X5X5X5XoX%.,.O 0XaXaXaXaXaXaXaXaXuX. ,.-.XX5XoX5X5XoXoX%.:.. 9XaX9X$ # ,.,.:.y.aXaXaXaXaXaX",
"aXaXaXtX-.,.,. .  ;XaXaXaX@X: ,.q.q.q.q.q.q.q.:.< N.pXaXaXaXaXaXaXaXaXaXP.: ,.q.q.q.q.q.q.q.:.1 G aXaXaX;X  ) ,.,.;.7XaXaXaXaXaX",
"aXaXaXW.:.,.,.: #XaXaXaXaXpX/ :.c c v v v c x ,.( 9XaXaXaXaXaXaXaXaXaXaXrXR :.W ~ ~ ~ ~ ~ W :.T 8XaXaXaXaX#X: :.,.:.c.aXaXaXaXaX",
"aXaXaX$.:.,.( F aXaXaXaXaX].;./ # @ @ # # # @ l ;.~.aXaXaXaXaXaXaXaXaXaX#X*.) + , , # # , # R *.].aXaXaXaXaXF / ,.:.#.aXaXaXaXaX",
"aXaX7X*.,.,.< -XaXaXaXaXpX9.:.> R.R.R.R.R.R.R.+ :.0.yXaXaXaXaXaXaXaXaXpX9.,.< R.U.U.U.R.U.R.: ,.6.pXaXaXaXaX-X> ,.,.*.3XaXaXaXaX",
"aXaX#X:.,.:.N pXaXaXaXaXW.;.k L aXaXaXaXaXaXaXD.s :.k.aXaXaXaXaXaXaXaX~.;.j J aXaXiXaXiXiXaXN.s :.x.aXaXaXaXaXM :.,.:.'.aXaXaXaX",
"aXaX^.:.,.;.V.aXaXaXaXtX1.:.. ;XaXaXaXaXaXaXaXrX$ o.&.6XaXaXaXaXaXaXeX0.,.O *XaXaXaXaXaXaXaX8XX *.1.tXaXaXaXaX}.&.,.:.W.aXaXaXaX",
"aXaX^.:.,.*.s.n.n.n.n.l.,.j D.aXaXaXaXaXaXaXaXaXK.s ,.l.!.b.!.b.b.!.l.,.j Z.aXaXaXaXaXaXaXaXaXD.k :.l.^.^.^.^.~.| ,.:.v.aXaXaXaX",
"aXaXW.:.,.*.&.&.&.&.&.*.,.M aXaXaXaXaXaXaXaXaXaXaXV *.*.<.=.=.<.<.=.&.,.m iXaXaXaXaXaXaXaXaXaXaXm *.*.6.0.%.5.5...,.:.v.aXaXaXaX",
"aXaXG.:.,.,.U Y U U U U :.p.aXaXaXaXaXaXaXaXaXaXaXH.*.R E U E U E E Y :.i.aXaXaXaXaXaXaXaXaXaXaXA.*.R E E E E W =.,.:.x.aXaXaXaX",
"aXaXS.,.,.:.n M i i p $ o.3.9XaXaXaXaXaXaXaXaXaXrXr.>.@ y t t t t y $ *.r.eXaXaXaXaXaXaXaXaXaXyXj.:., 8 9 9 9 t ,.,.:.i.aXaXaXaX",
"aXaXK.&.,.:.y.L.L.L.P.J k :.c.aXaXaXaXaXaXaXaXaX~.:.Y H D.A.A.A.A.D.H U :.~.aXaXaXaXaXaXaXaXaX~.:.T J i.I I P t.:.,.;.B.aXaXaXaX",
"aXaX-XY ,.:.<.rXaXaXaXaXw _ &.<XaXaXaXaXaXaXaX8Xo.X.- aXaXaXaXaXaXaXiX8 | o.1XaXaXaXaXaXaXaX9Xo.X.- aXpXaXiXpXj.:.,.( |.aXaXaXaX",
"aXaXaX= ,.,.:._.aXaXaXaXP.> :.g.tXyXrXrXrXrXyXx.:.s N.aXaXaXaXaXaXaXaXS.s :.x.tXyXyXyXyXyXtXW.:.k L aXaXaXaX$X;.,.,.a pXaXaXaXaX",
"aXaXaXB | ,.:.X.<XaXaXaXaXu } ,.Y.'.'.'.'.'.].>.} q aXaXaXaXaXaXaXaXaXpXw } ;. X+X+X+X+X+XOX*.} q aXaXaXaXrX$.:.,.o.9 aXaXaXaXaX",
"aXaXaX@X> ,.,.:.k.pXaXaXaX3X> ,.O.+.+.+.+.+.O.,.>  XaXaXaXaXaXaXaXaXaXaX X> :.o.=.=.=.=.=.+.:.> T.aXaXaXpX_.:.,.:.j K.aXaXaXaXaX",
"aXaXaXaX; o.,.,.:.+XpXaXaXwX;.*.q r r r r 4 q *.&.wXaXaXaXaXaXaXaXaXaXaXiXo.-.f b h h b b f -.| iXaXaXpX;X;.,.,.o.* aXaXaXaXaXaX",
"aXaXaXaX;X  *.,.,.:.#XiXaXs.:.d ; ; ; ; * ; ; s :.s.aXaXaXaXaXaXaXaXaXaXG.:.j ; ; ; ; * ; ; l :.J.aXaX3X*.,.,.;.  D.aXaXaXaXaXaX",
"aXaXaXaXaXt @ ;.,.,.,.Y.rX;.>.o iXaXiXaXaXpXpXo >.;.eXaXaXaXaXaXaXaXaXeX;.>.o aXiXaXpXaXaXpXo ;.*.iX4X*.:.,.:.g o aXaXaXaXaXaXaX",
"aXaXaXaXaXaXX 4 :.,.,.,.^ :.  -XaXaXaXaXaXaXaX-X  :.[ aXaXaXaXaXaXaXaX[ :.  @XaXaXaXaXaXaXaXT.o :.T :.,.,.:.Q   pXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXiX. 3 :.,.,.:.O.t pXaXaXaXaXaXaXaXaX& ..:.5XaXiXaXaXaXaX5X,.O.$ aXaXaXaXaXaXaXaXaX7 } :.,.,.:.c   0XaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaX9X  - ,.,.,.,.-.@..XaXaXaXaXaXaXaX0XO ,.<.#.#.#.#.#.#.<.,.O 0XaXaXaXaXaXaXaX5X[ -.;.,.,.:.r . =XaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaX;XX = _ :.,.,.;.2.4.G.6XaXaXaXaXaXM.;.:.;.;.;.;.;.;.;.*.M.aXaXaXaXaXtXY.[ 3.;.,.,.:.-.2 . ;XaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaX*Xw : 3 ,.,.,.,.;.2.w.4.Q.2XrXpXh.:.e y y w w w y 3 :.l.aXaX5X_.8.0.3.;.,.,.:.,.g > X *XaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaX*XF.X 1 g ,.:.,.,.,.-.1.e.e.{ O./ 2 q 8 m m m 8 ; _ #.7.9.e.3.*.,.,.:.:.:.W 4 @ K OXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXwXE.S o a f #.:.:.:.:.,.:.&.>.=. . . .@.@.@. ._ -.-.*.-.,.,.:.:.,.=.x f # w E.8XpXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXpX=XI.A $ 1 h c _ :.,.,.:.,.:.,.,.:.:.,.,.:.,.,.,.:.,.,.:.O.W b a @ p I.].aXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaX#XH.P 0 @ 1 g g v ` #.-.:.:.:.:.,.:.:.,.>.O.) W g g a , % H L.E.aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX9XP.D.P N $ * < a k k z z z z z z z k a 1 = $ y H D.F.*XaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX8XR.Z.Z.Z.H A N t 8 8 9 8 w i Z D I Z.C.I.*XaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXiX;XOXI.H.A.A.A.A.F.I.E.=XuXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX",
"aXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaXaX"
};
'''
        return XPM

    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
               Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
               to return a tuple of all serializable objects or None.'''
        return None

    def __setstate__(self,state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
               Since no data were serialized nothing needs to be done here.'''
        return None



if __name__ == "__main__":

    import os
    import FreeCAD, FreeCADGui, Part
    if ".FCMacro" in __file__ and not os.path.exists(__file__.replace(".FCMacro",".py")):
        current = __file__
        new_name = current.replace(".FCMacro", ".py")
        with open(new_name, "w") as new_file:
            with open(__file__, "r") as current_file:
                new_file.write(current_file.read())
        FreeCAD.Console.PrintWarning("A new file has been created named Honeycomb.py in order for Honeycomb objects to work when you reload a document containing a Honeycomb object.\n")
    import Honeycomb
    import importlib
    importlib.reload(Honeycomb)

    doc = FreeCAD.ActiveDocument if FreeCAD.ActiveDocument else FreeCAD.newDocument()
    body=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")
    if body:
        fp = doc.addObject("PartDesign::FeatureAdditivePython","Honeycomb")
    else:
        fp = doc.addObject("Part::FeaturePython","HoneyComb")
    Honeycomb.Honeycomb(fp)
    Honeycomb.HoneycombVP(fp.ViewObject)
    # selx = FreeCADGui.Selection.getSelection()
    # if selx:
    #     profile = selx[0]
    #     if hasattr(profile,"Shape"):
    #         fp.Profile = profile

    if body:
        body.addObject(fp)

    if not hasattr(fp,"Version") or fp.Version != __version__:
        FreeCAD.Console.PrintError(f"Version mismatch.  Version of Honeycomb.py is outdated.  New version is {__version__}.  You can delete Honeycomb.py from your macro folder, delete the newly created Honeycomb object, and re-run Honeycomb.FCMacro to recreate a new version.  Then save your file and restart FreeCAD to complete the update.\n")
