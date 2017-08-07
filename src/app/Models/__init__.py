from ..Controllers.FileManagerImpl import ModelFileReader
from .ModelImpl import ModelImpl
from astropy.coordinates import SphericalRepresentation as SR
import numpy as np 
from astropy import units as u
from .Parameters.Parameters import Parameters

class __Model(dict):
    """Wrapper of a dict instance, with added functionality for global values like earthVelocity"""
    def __init__(self):
        dict.__init__(self)
        self.addModel('default',Parameters())
        
    @property
    def earthVelocity(self):
        return SR(u.Quantity(265,'degree'),u.Quantity(48,'degree'),365)

    def addModel(self, modelID=None,parameters=None):
        if modelID and parameters:
            self[modelID] = ModelImpl(parameters)
        elif modelID:
            paramLoader = ModelFileReader()
            paramLoader.open()
            parameters = paramLoader.load(modelID)
            self[paramLoader.prettyString] = parameters
        elif parameters:
            self[self._generateName()] = ModelImpl(parameters)
        else:
            paramLoader = ModelFileReader()
            paramLoader.open()
            parameters = paramLoader.load()
            self[self._generateName()] = parameters

    def setUpdatable(self,model):
        for k,v in self.items():
            if k is model:
                v.dynamic = True
            else:
                v.dynamic = False

    def updateModel(self,modelID,parameters):
        if modelID in self:
            self[modelID].updateParameters(parameters)
        else:
            self.addModel(modelID = modelID, parameters=parameters)

    def DefaultModel(self):
        return ModelImpl(Parameters())


    def _generateName(self):
        return "default"



Model = __Model()
