

import numpy as np 

from .ModelImpl import ModelImpl
from app.Parameters.Parameters import Parameters


class __Model(dict):
    """Wrapper of a dict instance, with added functionality for global values like earthVelocity"""
    def __init__(self):
        dict.__init__(self)
        self.addModel('default',Parameters())
        
    def addModel(self, modelID=None,parameters=None):
        if modelID and parameters:
            self[modelID] = ModelImpl(parameters)
        elif modelID:
            from ..Controllers.FileManagerImpl import ModelFileReader
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
# Model = None#__Model()
