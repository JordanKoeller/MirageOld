class LightCurveParameters(object):
    
    def __init__(self, startPos, endPos, numDataPoints):
        self.pathStart = startPos
        self.pathEnd = endPos
        self.resolution = numDataPoints
        
    def __str__(self):
        return "LIGHTCURVE:\n\n Start = "+str(self.pathStart.to('arcsec'))+"\nEnd = "+str(self.pathEnd.to('arcsec'))+"\nResolution = "+str(self.resolution)+" pixels"