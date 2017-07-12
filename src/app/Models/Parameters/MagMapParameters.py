
class MagMapParameters(object):
    
    def __init__(self, center, dimensions, resolution):
        self.center = center
        self.dimensions = dimensions
        self.resolution = resolution
        
        
    def __str__(self):
        return "MAGNIFICATION MAP:\n\nCenter = " + str(self.center.to('arcsec')) + "\n Dimensions = " + str(self.dimensions.to('arcsec')) + "\n Resolution = "+str(self.resolution.x)+"x"+str(self.resolution.y)