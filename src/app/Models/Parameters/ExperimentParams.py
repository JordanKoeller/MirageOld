'''
Created on Jun 4, 2017

@author: jkoeller
'''
from enum import Enum



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


    def __init__(self,name = None, description = None, numTrials = 1, trialVariance = 1,resultParams = []):
        '''
        Constructor
        '''
        self.name = name
        self.description = description
        self.numTrials = numTrials
        self.trialVarianceFunction = trialVariance
        self.desiredResults = resultParams
        
        
    def generatePath(self,params):
        pass #Need to impliment
    
    def getParams(self,name):
        for i in self.desiredResults:
            if name == i.keyword:
                return i
        return None
    

    
    @property
    def desc(self):
        return self.description
        
    def __str__(self):
        string =  "Name = "+self.name+"\nDescription = "+self.desc+"\nNumber of Trials = "+str(self.numTrials)+"\n"
        for i in self.desiredResults:
            string += str(i)
        return string