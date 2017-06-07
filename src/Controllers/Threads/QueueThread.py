'''
Created on Jun 1, 2017

@author: jkoeller
'''
from PyQt5 import QtCore

from Models import Model
from Calculator.ExperimentResultCalculator import ExperimentResultCalculator


class QueueThread(QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals):
        '''
        Constructor
        '''
        
    def run(self, experimentQueue,filemanager):
        for params in experimentQueue:
            numTrials = params.extras.numTrials 
            filemanager.newExperiment(params) #NEED TO IMPLIMENT
            exptRunner = ExperimentResultCalculator(params)
            for expt in range(0,numTrials):
                params = params.extras.varyTrial(params) #NEED TO IMPLIMENT
                Model.updateParameters(params)
                data = exptRunner.runExperiment() #NEED TO IMPLIMENT
                filemanager.sendTrial(data)
            filemanager.closeExperiment()
        filemanager.flush()
        filemanager.close()
        
        
    def runTrial(self,params):
        Model.updateParameters(params)
        lightCurveData = Model.engine.makeLightCurve(params.quasarStartPos, params.quasarEndPos, params.extras.resolution)
        return lightCurveData
        
    