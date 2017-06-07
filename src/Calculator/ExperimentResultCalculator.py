'''
Created on Jun 6, 2017

@author: jkoeller
'''
from Models import Model
from Models.Parameters.ExperimentParams import ResultTypes


def __LIGHT_CURVE():
    pass
def __MAGMAP():
    pass
def __STARFIELD():
    pass
def __VIDEO():
    pass


class ExperimentResultCalculator(object):
    '''
    classdocs
    '''


    def __init__(self, parameters):
        '''
        Constructor
        '''
        expTypes = parameters.extras.desiredResults
        #Parse expTypes to functions to run.
        self.experimentRunners = []
        for exp in expTypes:
            if exp is ResultTypes.LIGHT_CURVE:
                self.experimentRunners.append(__LIGHT_CURVE)
            if exp is ResultTypes.MAGMAP:
                self.experimentRunners.append(__MAGMAP)
            if exp is ResultTypes.STARFIELD:
                self.experimentRunners.append(__STARFIELD)
            if exp is ResultTypes.VIDEO:
                self.experimentRunners.append(__VIDEO)
        
        
    def runExperiment(self):
        ret = []
        for exp in self.experimentRunners:
            ret.append(exp())
            