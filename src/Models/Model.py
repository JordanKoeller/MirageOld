'''
Created on Jun 1, 2017

@author: jkoeller
'''

import time


from Calculator.Engine.Engine_Grid import Engine_Grid as Engine


class __Model(object):
    def __init__(self):
        self.__Engine = Engine()
    
    def updateParameters(self,params):
        if self.parameters:
            params.setTime(self.parameters.time)
            params.quasar.setPos(self.parameters.quasar.observedPosition)
        self.__Engine.updateParameters(params)
        
    @property
    def parameters(self):
        return self.__Engine.parameters
    
    @property
    def engine(self):
        return self.__Engine
    
    def moveStars(self):
        if self.parameters.galaxy.hasStarVel:
            self.parameters.galaxy.moveStars(self.parameters.dt)
            self.__engine.reconfigure()
            
Model = __Model()

