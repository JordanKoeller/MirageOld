'''
Created on Jun 4, 2017

@author: jkoeller
'''
from Models.ExperimentQueue.Experiment import TrialVariance

class ExperimentParams(object):
    '''
    classdocs
    '''


    def __init__(self,name, description = None, numTrials = 1, trialVariance = 1, resolution=200,pathStart = None,pathEnd = None):
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
        
        
    def generatePath(self,params):
        pass #Need to impliment
        