'''
Created on Jun 6, 2017

@author: jkoeller
'''
import math

from Models import Model
from Models.Parameters.ExperimentParams import ResultTypes
from Utility import Vector2D
import numpy as np



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
            
            
    def varyTrial(self,params):
        return params
    
    def __LIGHT_CURVE(self):
        start,finish = (Model.parameters.extras.pathStart,Model.parameters.extras.pathEnd)
        res = Model.parameters.extras.resolution
        return Model.engine.makeLightCurve(start,finish,res)
    def __MAGMAP(self):
        start,finish = (Model.parameters.extras.pathStart,Model.parameters.extras.pathEnd)
        midpt = (start+finish)/2
        border = (finish-midpt).magnitude()*math.sqrt(2)
        topleft = midpt + Vector2D(-border,border)
        return Model.engine.makeMagMap(topleft,border*2,border*2,int(Model.parameters.extras.resolution*2*math.sqrt(2))) #Assumes args are (topleft,height,width,resolution)
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
            