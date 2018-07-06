'''
Created on Jun 4, 2017

@author: jkoeller
'''
import numpy as np
from astropy import units as u
from ..utility import Vector2D, Vector2DJSONDecoder, zeroVector
import math

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
            elif kind == "batch_lightcurve":
                decoder = BatchLightCurveJSONDecoder()
                resultParams.append(decoder.decode(data))
            elif kind == 'datafile':
                decoder = RDDFileInfoJSONDecoder()
                resultParams.append(decoder.decode(data))
        return ExperimentParams(name,desc,nt,tv,resultParams)

class ExperimentParams(dict):
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
        for i in self.desiredResults:
            self[i.keyword] = i
        
        
    def generatePath(self,params):
        pass #Need to impliment
    
    def getParams(self,name):
        for i in self.desiredResults:
            if name == i.keyword:
                return i
        return None
    
    def append(self,data):
        self[data.keyword] = data
    

    
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
    
    def update(self,start=None,end=None,resolution=None):
        if start:
            assert isinstance(start,Vector2D), "Start must be a Vector2D instance."
            self.pathStart = start
        if end:
            assert isinstance(end,Vector2D), "End must be a Vector2D instance."
            self.pathEnd = end
        if resolution:
            assert isinstance(resolution,int) and resolution > 1, "resolution must be an int, greater than 1"
            self.resolution = resolution


    def __str__(self):
        return "LIGHTCURVE:\n\n Start = "+str(self.pathStart.to('arcsec'))+"\nEnd = "+str(self.pathEnd.to('arcsec'))+"\nResolution = "+str(self.resolution)+" pixels"
    
class BatchLightCurveParameters(object):
    
    def __init__(self,num_curves,resolution,bounding_box,query_points = None,seed = None):
        assert isinstance(bounding_box,MagMapParameters)
        from mirage.preferences import GlobalPreferences
        self.num_curves = num_curves
        self.resolution = resolution
        self.bounding_box = bounding_box
        self._lines = query_points
        if seed:
            self._seed = seed
        else:
            self._seed = GlobalPreferences['light_curve_generator_seed']
        
        
    @property
    def keyword(self):
        return "batch_lightcurve"

    @property
    def seed(self):
        return self._seed
    
    
    @property
    def jsonString(self):
        encoder = BatchLightCurveJSONEncoder()
        return encoder.encode(self)

    def _slice_line(self,pts):
        #pts is an array of [x1,y1,x2,y2]
        #Bounding box is a MagMapParameters instance
        #resolution is a specification of angular separation per data point
        x1,y1,x2,y2 = pts
        m = (y2 - y1)/(x2 - x1)
        angle = math.atan(m)
        resolution = self.resolution.to('rad')
        dx = resolution.value*math.cos(angle)
        dy = resolution.value*math.sin(angle)
        dims = self.bounding_box.dimensions.to('rad')
        center = self.bounding_box.center.to('rad')
        lefX = center.x - dims.x/2
        rigX = center.x + dims.x/2
        topY = center.y + dims.y/2 
        botY = center.y - dims.y/2
        flag = True
        x = x1
        y = y1
        retx = [] 
        rety = [] 
        while flag:
            x -= dx
            y -= dy
            flag = x >= lefX and x <= rigX and y >= botY and y <= topY
        flag = True
        while flag:
            x += dx
            y += dy
            retx.append(x)
            rety.append(y)
            flag = x >= lefX and x <= rigX and y >= botY and y <= topY
        retx = retx[:-1]
        rety = rety[:-1]
        return [retx,rety]
    
    @property
    def lines(self):
        if self._lines:
            return self._lines
        else:
            rng = np.random.RandomState(self._seed)
            scaled = rng.rand(self.num_curves,4) - 0.5
            #np.random.rand returns an array of (number,4) dimension of doubles over interval [0,1).
            #I subtract 0.5 to center on 0.0
            center = self.bounding_box.center.to('rad')
            dims = self.bounding_box.dimensions.to('rad')
            width = dims.x
            height = dims.y
            scaled[:,0] *= width
            scaled[:,1] *= height
            scaled[:,2] *= width
            scaled[:,3] *= height
            scaled[:,0] += center.x
            scaled[:,1] += center.y
            scaled[:,2] += center.x
            scaled[:,3] += center.y
            # lines = u.Quantity(scaled,'rad')
            slices = map(lambda line: u.Quantity(np.array(self._slice_line(line)).T,'rad'),scaled)
            self._lines = list(slices)
            return self._lines
            
    
    def __str__(self):
        return "LIGHTCURVE BATCH:\n\n Count = "+str(self.num_curves)+"\n Resolution"+str(self.resolution)

class BatchLightCurveJSONEncoder():
    
    def __init__(self):
        pass
    
    def encode(self,obj):
        assert isinstance(obj,BatchLightCurveParameters)
        from mirage.utility import QuantityJSONEncoder
        res = {}
        res['num_curves'] = obj.num_curves
        qe = QuantityJSONEncoder()
        res['resolution'] = qe.encode(obj.resolution)
        res['bounding_box'] = obj.bounding_box.jsonString
        res['seed'] = obj.seed
        return res
    
class BatchLightCurveJSONDecoder():
     
    def __init__(self):
        pass 
     
    def decode(self,js):
        from mirage.utility import QuantityJSONDecoder
        qd = QuantityJSONDecoder()
        num_curves  = js['num_curves']
        resolution = qd.decode(js['resolution'])
        mmd = MagMapJSONDecoder()
        bounding_box = mmd.decode(js['bounding_box'])
        if 'query_points' in js:
            pts = None
            if js['query_points']:
                pts = qd.decode(js['query_points'])
            return BatchLightCurveParameters(num_curves,resolution,bounding_box,pts)
        if 'seed' in js:
            seed = js['seed']
            return BatchLightCurveParameters(num_curves,resolution,bounding_box,seed=seed)
        else:
            from mirage.preferences import GlobalPreferences
            seed = GlobalPreferences['light_curve_generator_seed']
            return BatchLightCurveParameters(num_curves,resolution,bounding_box)
            
         
class RDDFileInfo(object):
    """"Object for storing info about a GridRDD saved in a Scala
    object file, for use by a cluster."""
    def __init__(self, fname,num_partitions):
        super(RDDFileInfo, self).__init__()
        self.filename = fname
        self.num_partitions = num_partitions

    def set_numParts(self,nparts):
        self.num_partitions = nparts

    def set_filename(self,name):
        self.filename = name
        
    @property 
    def keyword(self):
        return "datafile"

    @property 
    def jsonString(self):
        return {"filename":self.filename,"num_partitions":self.num_partitions}

class RDDFileInfoJSONDecoder(object):
    def __init__(self):
        pass

    def decode(self,js):
        fname = js['filename']
        num_partitions = js['num_partitions']
        return RDDFileInfo(fname,num_partitions)


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
        ret = MagMapParameters(dims,res)
        ret.center = center
        return ret

class MagMapParameters(object):
    
    def __init__(self, dimensions, resolution):
        self.center = zeroVector
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