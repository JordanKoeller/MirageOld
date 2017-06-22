'''
Created on Jun 6, 2017

@author: jkoeller
'''
import math

from Models import Model
from Models.Parameters.ExperimentParams import ResultTypes
from Utility import Vector2D
import numpy as np
from Utility.NullSignal import NullSignal
# from Controllers.QueueController import defaultVariance
def defaultVariance(params,trialNo):
    print("Defaulting")
    return params

def varyTrial(params,trialNo):
    from astropy import units as u
    import copy
    varianceStr = params.extras.trialVarianceFunction
    oldParams = params
    nspace = {}
    exec(varianceStr,{'oldParams':oldParams,'trialNumber':trialNo,'u':u,'np':np,'copy':copy},nspace)
    return nspace['newParams']

class ExperimentResultCalculator(object):
    '''
    classdocs
    '''


    def __init__(self, parameters,signals = NullSignal):
        '''
        Constructor
        '''
        expTypes = parameters.extras.desiredResults
        self.signals = signals
        #Parse expTypes to functions to run.
        self.experimentRunners = []
        for exp in expTypes:
            if exp is ResultTypes.LIGHT_CURVE:
                self.experimentRunners.append(self.__LIGHT_CURVE)
            if exp is ResultTypes.MAGMAP:
                self.experimentRunners.append(self.__MAGMAP)
            if exp is ResultTypes.STARFIELD:
                self.experimentRunners.append(self.__STARFIELD)
#             if exp is ResultTypes.VIDEO:
#                 self.experimentRunners.append(self.__VIDEO)
        
        
    def runExperiment(self):
        ret = []
        for exp in self.experimentRunners:
            ret.append(exp())
        return ret

            

    
    def __LIGHT_CURVE(self):
        start,finish = (Model.parameters.extras.pathStart,Model.parameters.extras.pathEnd)
        res = Model.parameters.extras.resolution
        return Model.engine.makeLightCurve(start,finish,res)
        
    def __MAGMAP(self):
        start,finish = (Model.parameters.extras.pathStart,Model.parameters.extras.pathEnd)
        dims = finish - start 
        print("Starts at " + str(start))
        print("Size of "+ str(dims))
        return Model.engine.makeMagMap(start,dims,int(Model.parameters.extras.resolution),self.signals['progressBar'],self.signals['progressBarMax']) #Assumes args are (topleft,height,width,resolution)
        ################################## WILL NEED TO CHANGE TO BE ON SOURCEPLANE?????? ############################################################
    def __STARFIELD(self):
        stars = Model.parameters.galaxy.stars 
        retArr = np.ndarray((len(stars),3),np.float64)
        for i in range(0,len(stars)):
            x,y = stars[i].position.asTuple
            mass = stars[i].mass
            retArr[i] = stars[i] = (x,y,mass)
        return retArr
    def __VIDEO(self):
        pass################################### MAY IMPLIMENT LATER
            