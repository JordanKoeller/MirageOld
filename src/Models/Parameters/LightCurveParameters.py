class LightCurveParameters(object):
    
    def __init__(self, startPos, endPos, numDataPoints):
        self.pathStart = startPos
        self.pathEnd = endPos
        self.resolution = numDataPoints