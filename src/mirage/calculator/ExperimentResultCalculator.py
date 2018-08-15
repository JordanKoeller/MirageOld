'''
Created on Jun 6, 2017

@author: jkoeller
'''
import time

import numpy as np

from ..utility.NullSignal import NullSignal
from ..utility.ParametersError import ParametersError
from ..model import AbstractModel
from ..parameters import Simulation
def exptModelVariance(simulation:AbstractModel,trialNo) -> AbstractModel:
    return simulation

def varyTrial(simulation:AbstractModel,trialNo:int) -> AbstractModel:
    from astropy import units as u
    import copy
    varianceStr = simulation.experiments.trial_variance_function
    nspace = {}
    try:
        exec(varianceStr,{'old_simulation':simulation,'trial_number':trialNo,'u':u,'np':np,'copy':copy},nspace)
    except ParametersError as e:
        raise e
    except:
        print("What happened")
        raise SyntaxError
    return nspace['new_simulation']

class ExperimentResultCalculator(object):
    '''
    Object responsible for calculating result datasets when performing calculations based on input from an experiment table.

    Parses a parameters instance upon initialization and determines what calculations need to be performed. Then calls private member methods to perform those calculations. 
    '''


    def __init__(self, simulation:Simulation) -> None:
        '''
        Constructor. Parses parameters to determine what calculations need to be performed.

        Arguments:
        ==================

        parameters: parameters instance to be parsed. Based on parameters.extras field, will configure this ExperimentResultCalculator instance to run parameters's experiments.
        signals: (defualt NullSignal) dict. Signals to be emitted upon completions of various calculations. If none are provided, NullSignal is used, sending all text to standard
        output.
        '''
        from mirage.parameters.ExperimentParams import MagMapParameters, BatchLightCurveParameters
        self.experimentRunners = []
        for exp in simulation.experiments.values():
            if isinstance(exp,MagMapParameters):
                self.experimentRunners.append(self.__MAGMAP)
            if isinstance(exp,BatchLightCurveParameters):
                self.experimentRunners.append(self.__BATCH_LIGHTCURVE)
        
        
    def run_experiment(self,model:AbstractModel) -> list:
        '''
        Function to call to calculate results. Returns a list of the resultant data.
        '''
        ret = []
        for exp in range(0,len(self.experimentRunners)):
            ret.append(self.experimentRunners[exp](model))
        return ret

    def __MAGMAP(self,model:AbstractModel) -> np.ndarray:
        '''
        Internal Function. Instructs the engine to make a magnification map and returns the data.

        '''
        print("Now making magmap")
        special = model.experiments['magmap']
        ret = model.engine.make_mag_map(special.center,special.dimensions,special.resolution) #Assumes args are (topleft,height,width,resolution)
        return ret

    
    def __BATCH_LIGHTCURVE(self,model:AbstractModel) -> np.ndarray:
        print("Now tracing curves")
        special = model.experiments['batch_lightcurve']
        ret = model.engine.sample_light_curves(special.lines)
        return np.array(ret)
