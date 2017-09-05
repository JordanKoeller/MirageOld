'''
Created on Jul 23, 2017

@author: jkoeller
'''
from ...Models.Parameters.MagMapParameters import MagMapParameters
import numpy as np

from ...Models.ParametersError import ParametersError
from ...Utility.Vec2D import Vector2D


class MagnificationMap(object):
    '''
    classdocs
    '''


    def __init__(self, nparray,magMapParameters):
        '''
        Constructor
        '''
        self._magmap = nparray
        if isinstance(magMapParameters, MagMapParameters):
            self._mmp = magMapParameters
        else:
            raise ParametersError("""magMapParameters must be an instance of Parameters.MagMapParameters.
These Parameters can be extracted from a Parameters instance by calling 'parameters.extras.getParams['magmap']'.""")
    
    def __iter__(self):
        return self
    
    def __getitem__(self,ind1,ind2=None):
        if ind2:
            return self.values[ind1,ind2]
        else:
            return self.values[ind1]
        
    def getLightCurve(self,start,end):
        if isinstance(start, Vector2D) and isinstance(end, Vector2D):
            start = start.to('rad')
            end = end.to('rad')
            startP = self.angleToPixel(start)
            endP = self.angleToPixel(end)
            dx = endP.x-startP.x
            dy = endP.y - startP.y
#             print(dx)
#             print(dy)
            lgStep = max([abs(dx),abs(dy)])
#             print(lgStep)
            x = np.arange(startP.x,endP.x,dx/lgStep)
            y = np.arange(startP.y,endP.y,dy/lgStep)
            ret = np.array([self.values[int(x[i]),int(y[i])] for i in range(int(lgStep))])
            return ret         
        else:
            raise ValueError("Start and End must be Vector2D classes.")
    
    def angleToPixel(self,angle):
        return self._mmp.angleToPixel(angle)
    
    def pixelToAngle(self,pixel):
        return self.__mmp.pixelToAngle(pixel)
    
    @property
    def values(self):
        return self._magmap
    
    @property
    def center(self):
        return self._mmp.center
    
    @property
    def resolution(self):
        return self.__mmp.resolution 

    @property
    def dimensions(self):
        return self._mmp.dimensions
    
    def __str__(self):
        return str(self._mmp)