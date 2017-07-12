'''
Created on Jun 1, 2017

@author: jkoeller
'''



from ..Calculator.Engine.Engine_PointerGrid import Engine_PointerGrid as Engine_Grid
# from ..Calculator.Engine.Engine_ShapeGrid import Engine_ShapeGrid as Engine_Grid
from ..Calculator.Engine.Engine_BruteForce import Engine_BruteForce as Engine_Brute
# from Calculator.Engine.Engine_Grid import Engine_Grid as Engine_Grid
from PyQt5 import QtGui
from astropy import units as u
from astropy.coordinates import SphericalRepresentation as SR


class __Model(object):
    def __init__(self):
        self.__Engine = Engine_Grid()
        print("Brute Forcing")
        self.__colormap = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66), QtGui.qRgb(53,252,92)]
        #Index 0: Black
        #Index 1: Yellow
        #Index 2: White
        #Index 3: Blue
        #Index 4: Orange
        #Index 5: Green
        
    def updateParameters(self, params):
        if params.galaxy.starVelocityParams and isinstance(self.__Engine,Engine_Grid):
            self.__Engine = Engine_Brute()
            print("Brute Forcing")
        elif not params.galaxy.starVelocityParams and isinstance(self.__Engine,Engine_Brute):
            self.__Engine = Engine_Grid()
            print("Grid Structure")
        if self.parameters:
            if params.time != 0.0:
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

    @property
    def earthVelocity(self):
        return SR(u.Quantity(265,'degree'),u.Quantity(48,'degree'),365)
            
    @property
    def colorMap(self):
        return self.__colormap
Model = __Model()

