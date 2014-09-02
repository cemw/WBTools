import rhinoscriptsyntax as rs

import clr
clr.AddReference("system.Drawing")
import System
import System.Drawing
from os import rename
import collections
import time


class SortedDisplayDict(dict):
   def __str__(self):
       return "{" + ", ".join("%r: %r" % (key, self[key]) for key in sorted(self)) + "}"

class ViewAnalysis():
    
    def imagePixels(image):
        bmp = System.Drawing.Bitmap(image)
        pixels = [ bmp.GetPixel(x,y) for x in xrange( bmp.Width ) for y in xrange( bmp.Height ) ]
        return pixels
    
    def generateView(surfaces, addTexture = True ):
        #Setup
        path = rs.DocumentPath().strip('.3dm')
        sView = rs.ViewCameraTarget(rs.CurrentView())
        valueDict = {}
        rs.EnableRedraw(False)
        
        for i, srf in enumerate(surfaces):
            print 'calculating panel ', str(i+1), ' of ', len(surfaces)
            numPixel = 0
            rs.HideObject(srf)
            
            # Set camera to center of current surface and capture teh view to a file
            origin = rs.EvaluateSurface(srf, rs.SurfaceDomain(srf, 0)[1] / 2, rs.SurfaceDomain(srf, 1)[1] / 2)
            vector = rs.VectorScale(rs.SurfaceNormal(srf, [rs.SurfaceDomain(srf, 0)[1] / 2, rs.SurfaceDomain(srf, 1)[1] / 2]), 3000)
            target = rs.VectorCreate(origin, rs.VectorReverse(vector))
            
            rs.ViewCameraTarget(None, origin, target)
            rs.ViewCameraLens(None, 26)
            
            rs.Command(str('-ViewCaptureToFile ' + path + '_panel_' + str(i+1) + '.jpg width=' + str(int(rs.SurfaceDomain(srf, 0)[1])) + ' height ' + str(int(rs.SurfaceDomain(srf, 1)[1])) + ' enter'), False)
            rs.Sleep(4000)
            
            # Get and count red pixels
            pixels = imagePixels( path + '_panel_' + str(i+1) + ".jpg" )
            for pix in pixels:
                if rs.ColorRedValue(pix) > rs.ColorBlueValue(pix) + rs.ColorGreenValue(pix): numPixel += 1
            
            # Output change object name, add value to dictionary and apply texture to current surface 
            rs.ObjectName(srf, 'View Analys Panel ' + str(i+1) + ' - Score: ' + '{0:.1f}'.format( ( numPixel / len(pixels ) ) * 100) + '%')
            valueDict['panel ' + str(i+1)] = '{0:.1f}'.format( ( numPixel / len(pixels ) ) * 100) + '%'
            
            if addTexture:
                filename = path + '_panel_' + str(i+1) + '.jpg'
                rs.ObjectMaterialSource(srf, 1)
                if rs.ObjectMaterialIndex(srf) == -1: index = rs.AddMaterialToObject(srf)
                matname = rs.MaterialName(rs.ObjectMaterialIndex(srf), 'panel_' + str(i+1))
                rs.MaterialTexture(rs.ObjectMaterialIndex(srf), filename)
            
            rs.ShowObject(srf)
            
        #Reset viewcamera and update
        rs.ViewCameraTarget(rs.CurrentView(), sView[0], sView[1])
        rs.EnableRedraw(True)
        return SortedDisplayDict(valueDict)


if __name__ == "__main__":
    start = time.time()
    
    print generateView( rs.GetObjects('pick surfaces to evaluate', rs.filter.surface) )
    
    end = time.time()
    print "Run Time:", end-start