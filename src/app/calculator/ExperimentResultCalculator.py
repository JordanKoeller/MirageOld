'''
Created on Jun 6, 2017

@author: jkoeller
'''
import time

import numpy as np

from ..utility.NullSignal import NullSignal
from ..utility.ParametersError import ParametersError
# from ..Models import Model

# from Controllers.QueueController import exptModelVariance
def exptModelVariance(params,trialNo):
    print("exptModeling")
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
    Object responsible for calculating result datasets when performing calculations based on input from an experiment table.

    Parses a parameters instance upon initialization and determines what calculations need to be performed. Then calls private member methods to perform those calculations. 
    '''


    def __init__(self, parameters,signals = NullSignal):
        '''
        Constructor. Parses parameters to determine what calculations need to be performed.

        Arguments:
        ==================

        parameters: parameters instance to be parsed. Based on parameters.extras field, will configure this ExperimentResultCalculator instance to run parameters's experiments.
        signals: (defualt NullSignal) dict. Signals to be emitted upon completions of various calculations. If none are provided, NullSignal is used, sending all text to standard
        output.
        '''
        from app.parameters.ExperimentParams import MagMapParameters, LightCurveParameters, StarFieldData
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
        
        
    def runExperiment(self,model):
        '''
        Function to call to calculate results. Returns a list of the resultant data.
        '''
        ret = []
        from datetime import datetime as DT
        starttime = DT.now()
        for exp in range(0,len(self.experimentRunners)):
            ret.append(self.experimentRunners[exp](exp,model))
        endTime = DT.now()
        dSec = (endTime - starttime).seconds
        hrs = dSec // 3600
        mins = (dSec // 60) % 60
        secs = dSec % 60
        timeString = str(hrs)+" hours, " + str(mins) + " minutes, and " + str(secs) + " seconds"
        return ret


    
    def __LIGHT_CURVE(self,index,model):
        '''
        Internal Function. Instructs the engine to make a light curve and returns the data.
        '''
        special = model.parameters.extras.desiredResults[index]
        start,finish = (special.pathStart,special.pathEnd)
        res = special.resolution
        return model.engine.make_light_curve(start,finish,res)
        
    def __MAGMAP(self,index,model):
        '''
        Internal Function. Instructs the engine to make a magnification map and returns the data.

        '''
        special = model.parameters.extras.desiredResults[index]
        ret = model.engine.make_mag_map(special.center,special.dimensions,special.resolution) #Assumes args are (topleft,height,width,resolution)
#         rawMag = Model['exptModel'].engine.rawMagnification(special.center.to('rad').x,special.center.to('rad').y)
        return ret
        ################################## WILL NEED TO CHANGE TO BE ON SOURCEPLANE?????? ############################################################

    def __STARFIELD(self,index,model):
        return model.parameters.galaxy.stars 

    def __VIDEO(self):
        pass################################### MAY IMPLIMENT LATER
            
