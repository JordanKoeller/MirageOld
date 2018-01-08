'''
Created on Jan 8, 2018

@author: jkoeller
'''
from .CalculationDelegate import CalculationDelegate

import numpy as np 

from app.utility import Vector2D

class MagMapCalculationDelegate(CalculationDelegate):
    '''
    classdocs
    '''


    def __init__(self, parameters, magMapParameters, magMapArray):
        CalculationDelegate.__init__(self)
        self.reconfigure(parameters)
        self.magMapParameters = magMapParameters
        self.magMapArray = magMapArray.copy()
        self.__internalEngine = None

    def reconfigure(self,parameters):
        self._parameters = parameters
        if self.__internalEngine:
            self.__internalEngine.reconfigure()
    
    def make_light_curve(self,mmin, mmax, resolution):
        if self.__internalEngine:
            return self.__internalEngine.makeLightCurve_helper(mmin,mmax,resolution)
        else:
            pixels = self.makePixelSteps(mmin,mmax)
            retArr = np.ndarray(pixels.shape[0],dtype=np.float64)
            for index in range(pixels.shape[0]):
                value = self.magMapArray[int(round(pixels[index,0])),int(round(pixels[index,1]))]
                value = -2.5*np.log10(value)
                retArr[index] = value
            return retArr
            
    def make_mag_map(self,center, dims, resolution):
        raise NotImplementedError
    
    def get_frame(self,x, y, r):
        raise NotImplementedError
    
    def ray_trace(self):
        raise NotImplementedError
    
    def query_data_length(self, x, y, radius):
        raise NotImplementedError
    
    
    
    
    
    
    
    def makePixelSteps(self,mmin, mmax):
        if not isinstance(mmin,Vector2D):
            mmin = Vector2D(mmin[0],mmin[1])
        if not isinstance(mmax,Vector2D):
            mmax = Vector2D(mmax[0],mmax[1])
        pixelStart = mmin#self.magMapParameters.angleToPixel(mmin)
        pixelEnd = mmax#self.magMapParameters.angleToPixel(mmax)
        dx = pixelEnd.x - pixelStart.x
        dy = pixelEnd.y - pixelStart.y
        maxD = max(abs(dx),abs(dy))
        xPixels = np.arange(pixelStart.x,pixelEnd.x,dx/maxD)
        yPixels = np.arange(pixelStart.y,pixelEnd.y,dy/maxD)
        ret = np.ndarray((len(xPixels),2))
        ret[:,0] = xPixels
        ret[:,1] = yPixels
        return ret