'''
Created on Jun 4, 2017

@author: jkoeller
'''
from enum import Enum
import json


class ExperimentParamsJSONEncoder(object):
    """docstring for ExperimentParamsJSONEncoder"""
    def __init__(self):
        super(ExperimentParamsJSONEncoder, self).__init__()
        
    def encode(self,o):
        if isinstance(o,ExperimentParams):
            res = {}
            res['name'] = o.name
            res['description'] = o.description
            res['numTrials'] = o.numTrials
            res['trialVariance'] = str(o.trialVariance)
            res['resultList'] = map(lambda i:i.jsonString,o.desiredResults)
            return res
        else:
            raise TypeError("Attribute o must be of type ExperimentParams")
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

    @property
    def jsonString(self):
        encoder = ExperimentParamsJSONEncoder()
        return encoder.encode(self)
        
    def __str__(self):
        string =  "Name = "+self.name+"\nDescription = "+self.desc+"\nNumber of Trials = "+str(self.numTrials)+"\n"
        for i in self.desiredResults:
            string += str(i)
        return string