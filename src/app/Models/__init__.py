from ..Controllers.FileManagerImpl import ModelFileManager
from .ModelImpl import ModelImpl
from astropy.coordinates import SphericalRepresentation as SR
import numpy as np 
from astropy import units as u
from .Parameters.Parameters import Parameters

class __Model(dict):
    """Wrapper of a dict instance, with added functionality for global values like earthVelocity"""
    def __init__(self):
        dict.__init__(self)
        
    @property
    def earthVelocity(self):
        return SR(u.Quantity(265,'degree'),u.Quantity(48,'degree'),365)

    def addModel(self, name=None,parameters=None):
        if name and parameters:
            self[name] = ModelImpl(parameters)
        elif name:
            paramLoader = ModelFileManager()
            parameters = paramLoader.load(name)
            self[paramLoader.prettyString] = parameters
        elif parameters:
            self[self._generateName()] = ModelImpl(parameters)
        else:
            paramLoader = ModelFileManager()
            parameters = paramLoader.load()
            self[self._generateName()] = parameters

    def setUpdatable(self,model):
        for k,v in self.items():
            if k is model:
                v.dynamic = True
            else:
                v.dynamic = False

    def replaceModel(self,model):
        pass
        # self.clear()
        # for k,v in model.items():
        #     self[k] = v

    def updateModel(self,parameters):
        if len(self) is 0:
            self.addModel(parameters = parameters)
            self.setUpdatable('system_'+str(0))
        for k,model in self.items():
            if model.dynamic:
                model.updateParameters(parameters)

    def DefaultModel(self):
        return ModelImpl(Parameters())


    def _generateName(self):
        return "system_"+str(len(self))



Model = __Model()
