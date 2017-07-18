'''
Created on Jun 7, 2017

@author: jkoeller
'''

import copy
import math

from astropy.io import fits


import numpy as np

from ..Calculator.ExperimentResultCalculator import varyTrial
from ..Controllers.FileManagers.FITSFileManager import FITSFileManager
from ..Controllers.FileManagers.ParametersFileManager import ParametersFileManager
from ..Models.Parameters.LightCurveParameters import LightCurveParameters
from ..Models.Parameters.MagMapParameters import MagMapParameters
from ..Models.Parameters.StarFieldData import StarFieldData
from ..Utility.NullSignal import NullSignal
from .AbstractFileWrapper import AbstractFileWrapper


class Trial(AbstractFileWrapper):
    def __init__(self,filepath,trialno,fileobject=None,params=None,lookuptable=[]):
        AbstractFileWrapper.__init__(self, filepath, fileobject, params, lookuptable)    
        self.__trialNo = trialno

    def requiresDtype(dtype):
        def decorator(fn):
            def decorated(self,*args,**kwargs):
                for k,v in self._exptTypes.items():
                    if isinstance(k, dtype):
                        index = v
                        return fn(self,index,*args,**kwargs)
                raise AttributeError("Trial does not contain "+str(dtype) +" data.")
            return decorated
        return decorator
    
    
    
    @requiresDtype(LightCurveParameters)
    def getLightCurve(self,ind,xUnit = 'arcsec'): #Automatically passed in parameter 'ind' supplies information of what column that data type is located in
        lc = self._getDataSet(ind)
        x = np.arange(0,len(lc))
        distCovered = self.parameters.extras.pathEnd - self.parameters.extras.pathStart
        dist = distCovered.to(xUnit).magnitude()/len(lc)
        x = x * dist
        return (x,lc)
    
    
    @requiresDtype(MagMapParameters)
    def getFitsFile(self,ind,filename = None):
        arr = self._getDataSet(ind)
        if filename:
            fits.writeto(filename,arr)
        else:
            saver = FITSFileManager(NullSignal)
            saver.write(arr)
        print("Magnification Map saved")

    @requiresDtype(StarFieldData)
    def getStars(self,ind):
            return self._getDataSet(ind)

    @requiresDtype(StarFieldData)
    @requiresDtype(MagMapParameters)
    def superimpose_stars(self,magIndex,starsIndex,magmapimg=None,destination=None,color = (255,255,0,255)):
        parameters = self.regenerateParameters()
        from PIL import Image
        img = Image.open(magmapimg)
        pix = img.load()
        stars = parameters.galaxy.stars
        dTheta = parameters.extras.desiredResults[magIndex].dimensions.to('rad')/parameters.extras.desiredResults[magIndex].resolution
        starCoords = stars[:,0:2]
        starMass = stars[:,2]
        starCoords[:,0] = starCoords[:,0]/dTheta.x + parameters.extras.desiredResults[magIndex].resolution.x/2
        starCoords[:,1] = starCoords[:,1]/dTheta.y + parameters.extras.desiredResults[magIndex].resolution.y/2
        # starCoords[:,0] = starCoords[:,0]*dTheta.x/parameters.dTheta.to('rad').value
        # starCoords[:,1] = starCoords[:,1]*dTheta.y/parameters.dTheta.to('rad').value
        starCoords = np.ascontiguousarray(starCoords,dtype=np.int32)
        for row in range(0,starCoords.shape[0]):
            x,y = (starCoords[row,0],starCoords[row,1])
            mass = starMass[row]
            r = int(math.sqrt(mass+2))
            for i in range(x-r,x+r):
                for j in range(y-r,y+r):
                    if i >= 0 and i < parameters.extras.desiredResults[magIndex].resolution.x and j >= 0 and j < parameters.extras.desiredResults[magIndex].resolution.y:
                        pix[j,i] = color
        img.save(destination)
        print("Superimposed image saved as "+destination)

        
    @requiresDtype(StarFieldData)
    def regenerateParameters(self,ind,filename=None):
        params = copy.deepcopy(self.parameters)
        stars = self.getStars()
        params.setStars(stars)
        if filename:
            saver = ParametersFileManager(NullSignal)
            saver.write(params)
            print("Parameters Saved")
        else:
            return params
        
    @requiresDtype(StarFieldData)
    @requiresDtype(MagMapParameters)
    def traceQuasar(self,magIndex,starsIndex):
        magnifications = self._getDataSet(magIndex)
        params = self.regenerateParameters()
        return (magnifications,params)
        
    def saveParameters(self,filename=None):
        saver = ParametersFileManager(NullSignal)
        if filename:
            saver.write(copy.deepcopy(self.parameters),filename)
        else:
            saver.write(copy.deepcopy(self.parameters))
        print("parameters Saved")
        
    @property
    def trialNumber(self):
        return self.__trialNo

    @property
    def parameters(self):
        params = varyTrial(self._params,self.trialNumber)
        return params 

    
    
    @property
    def datasets(self):
        index = 0
        while index < self._lookupTable.shape[1]:
            yield self._getDataSet(self.__trialNo, index)
            
            
    def _getDataSet(self,tableNo):
            self._fileobject.seek(self._lookupTable[self.__trialNo,tableNo])
            return np.load(self._fileobject)