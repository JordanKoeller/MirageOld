'''
Created on Jun 6, 2017

@author: jkoeller
'''
import math

from ..Models.Model import Model
from ..Models.Parameters.ExperimentParams import ResultTypes
from ..Utility import Vector2D
import numpy as np
from ..Utility.NullSignal import NullSignal
from ..Models.Parameters.MagMapParameters import MagMapParameters
from ..Models.Parameters.LightCurveParameters import LightCurveParameters
from ..Models.ParametersError import ParametersError
from ..Models.Parameters.StarFieldData import StarFieldData

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
    try:
        exec(varianceStr,{'oldParams':oldParams,'trialNumber':trialNo,'u':u,'np':np,'copy':copy},nspace)
    except ParametersError as e:
        raise e
    except:
        print("What happened")
        raise SyntaxError
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
            if isinstance(exp, LightCurveParameters):
                self.experimentRunners.append(self.__LIGHT_CURVE)
            if isinstance(exp,MagMapParameters):
                self.experimentRunners.append(self.__MAGMAP)
            if isinstance(exp,StarFieldData):
                self.experimentRunners.append(self.__STARFIELD)
#             if exp is ResultTypes.STARFIELD:
#                 self.experimentRunners.append(self.__STARFIELD)
#             if exp is ResultTypes.VIDEO:
#                 self.experimentRunners.append(self.__VIDEO)
        
        
    def runExperiment(self):
        ret = []
        for exp in range(0,len(self.experimentRunners)):
            ret.append(self.experimentRunners[exp](exp))
        print("Experiment Finished")
        return ret

            

    
    def __LIGHT_CURVE(self,index):
        special = Model.parameters.extras.desiredResults[index]
        start,finish = (special.pathStart,special.pathEnd)
        res = special.resolution
        return Model.engine.makeLightCurve(start,finish,res)
        
    def __MAGMAP(self,index):
        special = Model.parameters.extras.desiredResults[index]
        Model.parameters.extras.desiredResults[index].center = Model.engine.getCenterCoords()
        return Model.engine.makeMagMap(special.center,special.dimensions,special.resolution,self.signals['progressBar'],self.signals['progressBarMax']) #Assumes args are (topleft,height,width,resolution)
        ################################## WILL NEED TO CHANGE TO BE ON SOURCEPLANE?????? ############################################################

    def __STARFIELD(self,index):
        return Model.parameters.galaxy.stars 

    def __VIDEO(self):
        pass################################### MAY IMPLIMENT LATER
            