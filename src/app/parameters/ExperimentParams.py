'''
Created on Jun 4, 2017

@author: jkoeller
'''
import numpy as np

from ..utility import Vector2D, Vector2DJSONDecoder


class ExperimentParamsJSONEncoder(object):
    """docstring for ExperimentParamsJSONEncoder"""
    def __init__(self):
        super(ExperimentParamsJSONEncoder, self).__init__()
        
    def encode(self,o):
        if isinstance(o,ExperimentParams):
            res = {}
            res['name'] = o.name
            res['description'] = o.description
            res['numTrials'] = o.numTrials
            res['trialVariance'] = str(o.trialVarianceFunction)
            results = {}
            for i in o.desiredResults:
                results[i.keyword] = i.jsonString
            res['resultList'] = results
            return res
        else:
            raise TypeError("Attribute o must be of type ExperimentParams")

class ExperimentParamsJSONDecoder(object):
    def __init__(self):
        pass

    def decode(self,o):
        name = o['name']
        desc = o['description']
        nt = o['numTrials']
        tv = o['trialVariance']
        resultParams = []
        for kind,data in o['resultList'].items():
            if kind == 'magmap':
                decoder = MagMapJSONDecoder()
                resultParams.append(decoder.decode(data))
            elif kind == 'lightcurve':
                decoder = LightCurveJSONDecoder()
                resultParams.append(decoder.decode(data))
            elif kind == 'starfield':
                resultParams.append(StarFieldData())
        return ExperimentParams(name,desc,nt,tv,resultParams)
class ExperimentParams(object):
    '''
    classdocs
    '''


    def __init__(self,name = None, description = None, numTrials = 1, trialVariance = 1,resultParams = []):
        '''
        Constructor
        '''
        self.name = name
        self.description = description
        self.numTrials = numTrials
        self.trialVarianceFunction = trialVariance
        self.desiredResults = resultParams
        
        
    def generatePath(self,params):
        pass #Need to impliment
    
    def getParams(self,name):
        for i in self.desiredResults:
            if name == i.keyword:
                return i
        return None
    

    
    @property
    def desc(self):
        return self.description

    @property
    def jsonString(self):
        encoder = ExperimentParamsJSONEncoder()
        return encoder.encode(self)
        
    def __str__(self):
        string =  "Name = "+self.name+"\nDescription = "+self.desc+"\nNumber of Trials = "+str(self.numTrials)+"\n"
        for i in self.desiredResults:
            string += str(i)
        return string
    

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
        
class LightCurveJSONDecoder(object):
    
    def __init__(self):
        pass
    
    def decode(self,data):
        vd = Vector2DJSONDecoder()
        start = vd.decode(data['pathStart'])
        end = vd.decode(data['pathEnd'])
        res = data['resolution']
        return LightCurveParameters(start,end,res)

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
    

class MagMapJSONEncoder(object):
    """docstring for MagMapJSONEncoder"""
    def __init__(self):
        super(MagMapJSONEncoder, self).__init__()
    def encode(self,o):
        if isinstance(o, MagMapParameters):
            res = {}
            res['center'] = o.center.jsonString
            res['dimensions'] = o.dimensions.jsonString
            res['resolution'] = o.resolution.jsonString
            return res
        else:
            raise TypeError("Argument o must be of type MagMapParameters.")
        
class MagMapJSONDecoder(object):
    
    def __init__(self):
        pass
    
    def decode(self,data):
        vd = Vector2DJSONDecoder()
        center = vd.decode(data['center'])
        dims = vd.decode(data['dimensions'])
        res = vd.decode(data['resolution'])
        ret = MagMapParameters(center,dims,res)
        return ret

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
        
    @property
    def jsonString(self):
        encoder = MagMapJSONEncoder()
        return encoder.encode(self)

        
        
    def __str__(self):
        return "MAGNIFICATION MAP:\n\nCenter = " + str(self.center.to('arcsec')) + "\n Dimensions = " + str(self.dimensions.to('arcsec')) + "\n Resolution = "+str(self.resolution.x)+"x"+str(self.resolution.y)
    
class StarFieldData(object):
    """docstring for StarFieldData"""
    def __init__(self):
        super(StarFieldData, self).__init__()
        
    @property
    def keyword(self):
        return "starfield"

    @property
    def jsonString(self):
        return []
        
    def __str__(self):
        return ""