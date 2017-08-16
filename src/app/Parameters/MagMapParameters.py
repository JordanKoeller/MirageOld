import numpy as np

from ..Utility.Vec2D import Vector2D


class MagMapParameters(object):
    
    def __init__(self, center, dimensions, resolution):
        self.center = center
        self.dimensions = dimensions
        self.resolution = resolution
        
    def pixelToAngle(self,pixel):
        dTheta = self.dimensions.to('rad')/self.resolution
        if isinstance(pixel,np.ndarray):
            pixel[:,0] = (pixel[:,0] - self.resolution.x/2)*dTheta.x + self.center.to('rad').x 
            pixel[:,1] = ( self.resolution.y/2 - pixel[:,1])*dTheta.y + self.center.to('rad').y
            return pixel
        else:
            pixel = Vector2D(pixel.x - self.resolution.x/2,self.resolution.y/2 - pixel.y)
            delta = pixel*dTheta
            return delta + self.center.to('rad')
    
    def angleToPixel(self,angle):
        dTheta = self.dimensions.to('rad')/self.resolution
        if isinstance(angle, np.ndarray):
            angle[:,0] = (angle[:,0] - self.center.to('rad').x)/dTheta.x + self.resolution.x/2
            angle[:,1] = self.resolution.y/2 - (angle[:,1] - self.center.to('rad').y)/dTheta.y
            return np.array(angle,dtype=np.int)
        else:
            delta = angle - self.center.to('rad')
            pixel = (delta/dTheta).unitless()
            return Vector2D(int(pixel.x + self.resolution.x/2),int(self.resolution.y/2 - pixel.y))
    
    @property
    def keyword(self):
        return "magmap"
        
        
        
    def __str__(self):
        return "MAGNIFICATION MAP:\n\nCenter = " + str(self.center.to('arcsec')) + "\n Dimensions = " + str(self.dimensions.to('arcsec')) + "\n Resolution = "+str(self.resolution.x)+"x"+str(self.resolution.y)