'''
Created on Jun 1, 2017

@author: jkoeller
'''



from PyQt5 import QtGui

import numpy as np

#from ..Calculator.Engine.Engine_BruteForce import Engine_BruteForce as Engine_Brute
<<<<<<< HEAD
from ..Calculator.Engine.Engine_ScalaSpark import Engine_Spark as Engine_Grid
=======
# if __name__ == '__main__':
#     # from ..Calculator.Engine.Engine_ScalaSpark import Engine_Spark as Engine_Grid
# else:
#     from ..Calculator.Engine.Engine_PointerGrid import Engine_PointerGrid as Engine_Grid
from ..Calculator.Engine.Engine_PointerGrid import Engine_PointerGrid as Engine_Grid
    
>>>>>>> 1c33bfba87ea6ba14d111255c64b1892746c3cd4
# from ..Calculator.Engine.Engine_Windowed import Engine_Windowed as Engine_Grid
from ..Utility.Partitioner.ColumnPartitioner import ColumnPartitioner
from ..Utility.Partitioner.RDDGrid import RDDGrid
from ..Utility.GridWrapper import construct as PointerGridWrapper


# from ..Calculator.Engine.Engine_ShapeGrid import Engine_ShapeGrid as Engine_Grid
# from Calculator.Engine.Engine_Grid import Engine_Grid as Engine_Grid
class ModelImpl(object):

    __colormap = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66), QtGui.qRgb(53,252,92)]
    __colorMapArr = np.array([[0,0,0],[255,255,0],[255,255,255],[50,101,255],[244,191,66],[53,252,92]],dtype=np.uint8)
    #Index 0: Black
    #Index 1: Yellow
    #Index 2: White
    #Index 3: Blue
    #Index 4: Orange
    #Index 5: Green
    

    def __init__(self,parameters=None):
        rddGrid = RDDGrid(ColumnPartitioner(),PointerGridWrapper)
        self.__Engine = Engine_Grid()
        self.dynamic = False
        if parameters:
            self.updateParameters(parameters)
        
    def updateParameters(self, params=None,*args,**kwargs):
        if not params:
            self.parameters.update(*args,**kwargs)
            params = self.parameters
        if params.galaxy.starVelocityParams and isinstance(self.__Engine,Engine_Grid):
            pass
#            self.__Engine = Engine_Brute()
        elif not params.galaxy.starVelocityParams:# and isinstance(self.__Engine,Engine_Brute):
            rddGrid = RDDGrid(ColumnPartitioner(),PointerGridWrapper)
            self.__Engine = Engine_Grid(rddGrid)
        if self.parameters:
            if self.parameters.time != 0.0:
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

    def reset(self):
        self.parameters.setTime(0)

    @property
    def colorMap(self):
        return self.__colormap
    
    @property
    def colorMap_arr(self):
        return self.__colorMapArr

