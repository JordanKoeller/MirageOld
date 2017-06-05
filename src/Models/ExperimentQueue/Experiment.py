'''
Created on Jun 1, 2017

@author: jkoeller
'''

from enum import Enum

class TrialVariance(Enum):
    Nothing = 1
    StarField = 2
    Path = 3
    StarFieldAndPath = 6

class Experiment(object):
    '''
    classdocs
    '''

    parameters = None
    name = None
    desc = None
    numTrials = 1
    
    

    def __init__(self, params):
        '''
        Constructor
        '''
        self.parameters = params
        self.name =          params.extras.name
        self.numTrials =     params.extras.numTrials
        self.trialVariance = params.extras.trialVariance
        if params.extras.description:
            self.desc = params.extras.description
        else:
            self.desc = self.name
            
        
    def calculate(self):
        self.hasResult = True
        
    def edit(self):
        print("Now editing "+self.name)
        
    def varyTrial(self,params):
        if self.trialVariance.value == 1:
            return params
        else:
            if self.trialVariance.value % 2 == 0:
                params.galaxy.clearStars()
                params.generateStars()
            if self.trialVariance % 3 == 0:
                params.extras.generatePath(params)
            return params
        
