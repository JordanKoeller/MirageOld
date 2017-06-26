'''
Created on Jun 7, 2017

@author: jkoeller
'''

import copy

from astropy.io import fits
from astropy import units as u

from Controllers.FileManagers.FITSFileManager import FITSFileManager
from Models.Parameters.ExperimentParams import ResultTypes
from Models.Stellar import PointLenser
from Utility.NullSignal import NullSignal
from Utility.Vec2D import Vector2D
from lens_analysis.AbstractFileWrapper import AbstractFileWrapper
import numpy as np
from Controllers.FileManagers.ParametersFileManager import ParametersFileManager
from Calculator.ExperimentResultCalculator import varyTrial
from Models.Parameters.MagMapParameters import MagMapParameters
from Models.Parameters.LightCurveParameters import LightCurveParameters

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
        
    @requiresDtype(ResultTypes.STARFIELD)
    def regenerateParameters(self,ind,filename=None):
        params = copy.deepcopy(self._params)
        stars = self._getDataSet(ind)
        starlist = []
        for i in range(stars.shape[0]):
            x,y,m = stars[i]
            starlist.append(PointLenser(Vector2D(x,y,'rad'),u.Quantity(m,'solMass')))
        params.setStars(starlist)
        if filename:
            saver = ParametersFileManager(NullSignal)
            saver.write(params)
            print("Parameters Saved")
        else:
            return params
    
    @requiresDtype(ResultTypes.STARFIELD) #Should be the second argument????
    @requiresDtype(ResultTypes.MAGMAP)
    def testFails(self,ind1,ind2):
        print(ind1)
        print(ind2)
        
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