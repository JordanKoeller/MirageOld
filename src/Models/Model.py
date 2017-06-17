'''
Created on Jun 1, 2017

@author: jkoeller
'''



from Calculator.Engine.Engine_PointerGrid import Engine_PointerGrid as Engine_Pointer
from Calculator.Engine.Engine_ShapeGrid import Engine_ShapeGrid as Engine_Shape
from Calculator.Engine.Engine_Grid import Engine_Grid as Engine_Grid
from Calculator.Engine.Engine_BruteForce import Engine_BruteForce as Engine_Brute


class __Model(object):
    def __init__(self):
        self.__Engine = Engine_Pointer()
    
    def updateParameters(self, params):
        if self.parameters:
            params.setTime(self.parameters.time)
            params.quasar.setPos(self.parameters.quasar.observedPosition)
            if params.galaxy.starVelocityParams:
                self.__Engine = Engine_Brute()
                print("Brute Forcing")
            else:
                self.__Engine = Engine_Pointer()
                print("Grid Structure")
        self.__Engine.updateParameters(params)
        
    @property
    def parameters(self):
        return self.__Engine.parameters
    
    @property
    def engine(self):
        return self.__Engine
    
    def moveStars(self):
        if self.parameters.galaxy.starVelocityParams != None:
            self.parameters.galaxy.moveStars(self.parameters.dt)
            self.__Engine.reconfigure()
            
Model = __Model()

