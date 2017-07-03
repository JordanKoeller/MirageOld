'''
Created on Jun 1, 2017

@author: jkoeller
'''



from Calculator.Engine.Engine_PointerGrid import Engine_PointerGrid as Engine_Grid
# from Calculator.Engine.Engine_ShapeGrid import Engine_ShapeGrid as Engine_Grid
from Calculator.Engine.Engine_BruteForce import Engine_BruteForce as Engine_Brute
# from Calculator.Engine.Engine_Grid import Engine_Grid as Engine_Grid


class __Model(object):
    def __init__(self):
        self.__Engine = Engine_Grid()
        print("Brute Forcing")
    
    def updateParameters(self, params):
        if params.galaxy.starVelocityParams and isinstance(self.__Engine,Engine_Grid):
            self.__Engine = Engine_Brute()
            print("Brute Forcing")
        elif not params.galaxy.starVelocityParams and isinstance(self.__Engine,Engine_Brute):
            self.__Engine = Engine_Grid()
            print("Grid Structure")
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
        if self.parameters.galaxy.starVelocityParams != None:
            self.parameters.galaxy.moveStars(self.parameters.dt)
            self.__Engine.reconfigure()
            
Model = __Model()

