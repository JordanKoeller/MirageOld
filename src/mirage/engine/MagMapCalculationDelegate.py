'''
Created on Jan 8, 2018

@author: jkoeller
'''
from .CalculationDelegate import CalculationDelegate

import numpy as np 

from mirage.utility import Vector2D

class MagMapCalculationDelegate(CalculationDelegate):
    '''
    classdocs
    '''


    def __init__(self, parameters, magMapParameters, magMapArray):
        CalculationDelegate.__init__(self)
        self._internal_engine = None
        self.reconfigure(parameters)
        self.magMapParameters = magMapParameters
        self.magMapArray = magMapArray.copy()

    def reconfigure(self,parameters):
        self._parameters = parameters
        if self._internal_engine:
            self._internal_engine.reconfigure()
    
    def make_light_curve(self,mmin, mmax, resolution):
        if self._internal_engine:
            return self._internal_engine.makeLightCurve_helper(mmin,mmax,resolution)
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
        return self.query_data_length(x, y, r)
    
    def ray_trace(self):
        raise NotImplementedError
    
    def query_data_length(self, x, y, radius):
        xy = Vector2D(x,y,'rad')
        xy = self.magMapParameters.angleToPixel(xy)
#         assert radius == self._parameters.queryQuasarRadius, "MagMap cannot query a radius different from that used to generate it."
        x = int(round(xy.x))
        y = int(round(xy.y))
        ret = self.magMapArray[x,y]
        return ret
    
    
    def makePixelSteps(self,mmin, mmax):
        if not isinstance(mmin,Vector2D):
            mmin = Vector2D(mmin[0],mmin[1])
        if not isinstance(mmax,Vector2D):
            mmax = Vector2D(mmax[0],mmax[1])
        pixelStart = self.magMapParameters.angleToPixel(mmin)
        pixelEnd = self.magMapParameters.angleToPixel(mmax)
        dx = pixelEnd.x - pixelStart.x
        dy = pixelEnd.y - pixelStart.y
        maxD = max(abs(dx),abs(dy))
        xPixels = np.arange(pixelStart.x,pixelEnd.x,dx/maxD)
        yPixels = np.arange(pixelStart.y,pixelEnd.y,dy/maxD)
        ret = np.ndarray((len(xPixels),2))
        ret[:,0] = xPixels
        ret[:,1] = yPixels
        return ret