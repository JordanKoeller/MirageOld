'''
Created on Jun 4, 2017

@author: jkoeller
'''
from enum import Enum

from Models.ExperimentQueue.Experiment import TrialVariance


class ResultTypes(Enum):
    LIGHT_CURVE = 1
    MAGMAP = 2
    STARFIELD = 3
    NOTHING = -1
#     VIDEO = 4

class ExperimentParams(object):
    '''
    classdocs
    '''


    def __init__(self,name, description = None, numTrials = 1, trialVariance = 1, resolution=200,pathStart = None,pathEnd = None,desiredResults = [ResultTypes.LIGHT_CURVE]):
        '''
        Constructor
        '''
        self.pathStart = pathStart
        self.pathEnd = pathEnd
        self.resolution = resolution
        self.name = name
        self.description = description
        self.numTrials = numTrials
        self.trialVariance = TrialVariance(trialVariance)
        self.resolution = resolution
        self.desiredResults = desiredResults
        
        
    def generatePath(self,params):
        pass #Need to impliment
    

    
    @property
    def desc(self):
        return self.description
        
    def __str__(self):
        return "Name = "+self.name+"\nDescription = "+self.desc+"\nNumber of Trials = "+str(self.numTrials)+"\n"