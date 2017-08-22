import json

class LightCurveJSONEncoder(object):
	"""docstring for LightCurveJSONEncoder"""
	def __init__(self):
		super(LightCurveJSONEncoder, self).__init__()
	
	def encode(self,o):
		if isinstance(o, LightCurveParameters):
			res = {}
			res['pathStart'] = o.pathStart.jsonString
			res['pathEnd'] = o.pathEnd.jsonString
			res['resolution'] = o.resolution
			return res
		else:
			raise TypeError("Argument o must be of type LightCurveParameters")

class LightCurveParameters(object):
    
    def __init__(self, startPos, endPos, numDataPoints):
        self.pathStart = startPos
        self.pathEnd = endPos
        self.resolution = numDataPoints
        
    @property
    def keyword(self):
        return "lightcurve"
        
    @property
    def jsonString(self):
        encoder = LightCurveJSONEncoder()
        return encoder.encode(self)


    def __str__(self):
        return "LIGHTCURVE:\n\n Start = "+str(self.pathStart.to('arcsec'))+"\nEnd = "+str(self.pathEnd.to('arcsec'))+"\nResolution = "+str(self.resolution)+" pixels"