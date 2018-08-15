'''
Created on Jun 4, 2017

@author: jkoeller
'''
import numpy as np
from astropy import units as u
import math

from ..utility import Vector2D, zeroVector, JSONable, QuantityJSONEncoder, \
    QuantityJSONDecoder, Region, PixelRegion
from .Parameters import Parameters



class ExperimentParams(dict,JSONable):
    '''
    classdocs
    '''


    def __init__(self,name:str = "",
        description:str = "",
        num_trials:int = 1,
        trial_variance:str = "",
        result_params:list = []) -> None:
        '''
        Constructor
        '''
        dict.__init__(self)
        JSONable.__init__(self)
        self._name = name
        self._description = description
        self._num_trials = num_trials
        self._trial_variance_function = trial_variance
        for i in result_params:
            self[i.keyword] = i

    @property
    def name(self) ->str:
        return self._name
    
    @property
    def description(self) ->str:
        return self._description
    @property
    def num_trials(self)->int:
        return self._num_trials
    @property
    def trial_variance_function(self)->str:
        return self._trial_variance_function
    
    def append(self,data):
        self[data.keyword] = data
    

    
    @property
    def desc(self):
        return self.description

    @classmethod
    def from_json(cls,js):
        name = js['name']
        desc = js['description']
        nt = js['num_trials']
        tv = js['trial_variance']
        resultParams = []
        for kind,data in js['result_list'].items():
            if kind == 'magmap':
                ps = MagMapParameters.from_json(data)
                resultParams.append(ps)
            elif kind == "batch_lightcurve":
                ps = BatchLightCurveParameters.from_json(data)
                resultParams.append(ps)
        return cls(name,desc,nt,tv,resultParams)

    @property
    def json(self) -> dict:
        res = {}
        res['name'] = self.name
        res['description'] = self.description
        res['num_trials'] = self.num_trials
        res['trial_variance'] = str(self.trial_variance_function)
        results = {}
        for keyword,params in self.items():
            results[keyword] = params.json
        res['result_list'] = results
        return res
        
    def __repr__(self):
        string =  "Name = "+self.name+"\nDescription = "+self.desc+"\nNumber of Trials = "+str(self.num_trials)+"\n"
        for i in self:
            string += str(i)
        return string
    
class Simulation(JSONable):

    def __init__(self,parameters:Parameters, experiments:ExperimentParams) -> None:
        self.parameters = parameters
        self.experiments = experiments

    @classmethod
    def from_json(cls,js):
        from mirage.utility import QuantityJSONDecoder
        qd = QuantityJSONDecoder()
        qz = js['parameters']['quasar']['z']
        gz = js['parameters']['galaxy']['z']
        q_mass = qd.decode(js['parameters']['quasar']['mass'])
        pt_mass = 0.5 * u.solMass
        specials = Parameters.static_special_units(pt_mass,q_mass,gz,qz)
        with u.add_enabled_units(specials):
            p = Parameters.from_json(js['parameters'])
            ex = ExperimentParams.from_json(js['experiments'])
            return cls(p,ex)

    @property
    def json(self) -> dict:
        ret = {}
        ret['parameters'] = self.parameters.json
        ret['experiments'] = self.experiments.json
        return ret

class BatchLightCurveParameters(JSONable):
    
    def __init__(self,
        num_curves:int,
        resolution:u.Quantity,
        region:Region,
        query_points:np.ndarray = None,
        seed:int = None) -> None:
        self.num_curves = num_curves
        self.resolution = resolution
        self.bounding_box = region
        self._lines = query_points
        if seed:
            self._seed = seed
        else:
            from mirage.preferences import GlobalPreferences
            self._seed = GlobalPreferences['light_curve_generator_seed']
        
        
    @property
    def keyword(self) -> str:
        return "batch_lightcurve"

    @property
    def seed(self) -> int:
        return self._seed
    
    @classmethod
    def from_json(cls,js):
        qd = QuantityJSONDecoder()
        nc = js['num_curves']
        bb = Region.from_json(js['bounding_box'])
        resolution = qd.decode(js['resolution'])
        seed = js['seed']
        return cls(nc,resolution,bb,seed=seed)
    
    @property
    def json(self) -> dict:
        qe = QuantityJSONEncoder()
        ret = {}
        ret['num_curves'] = self.num_curves
        ret['bounding_box'] = self.bounding_box.json
        ret['seed'] = self.seed
        ret['resolution'] = qe.encode(self.resolution)
        return ret

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


class MagMapParameters(PixelRegion):

    def __init__(self,*args,**kwargs):
        PixelRegion.__init__(self,*args,**kwargs)

    @property
    def keyword(self) -> str:
        return "magmap"
    
    def __str__(self):
        return "MAGNIFICATION MAP:\n\nCenter = " + str(self.center.to('arcsec')) + "\n Dimensions = " + str(self.dimensions.to('arcsec')) + "\n Resolution = "+str(self.resolution.x)+"x"+str(self.resolution.y)