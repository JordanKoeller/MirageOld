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


    def __init__(self, signals, experimentQueue,filemanager):
        '''
        Constructor
        '''
        QtCore.QThread.__init__(self)
        filemanager.getDirectory()
        self.experimentQueue = experimentQueue
        self.filemanager = filemanager
        self.signals = signals
        
    def run(self):
        ctr = 0
        for params in self.experimentQueue:
            ctr += 1
            numTrials = params.extras.numTrials 
            self.filemanager.newExperiment(params) #NEED TO IMPLIMENT
            exptRunner = ExperimentResultCalculator(params,self.signals)
            tc = 0
            for expt in range(0,numTrials):
                self.signals['progressLabel'].emit("Processing trial "+str(tc+1) +" of " + str(numTrials+1) + ".")
                tc += 1
                params = exptRunner.varyTrial(params) #NEED TO IMPLIMENT
                Model.updateParameters(params)
                data = exptRunner.runExperiment() #NEED TO IMPLIMENT
                self.filemanager.sendTrial(data)
            self.filemanager.closeExperiment()
        self.filemanager.flush()
        self.filemanager.close()
        self.signals['progressLabel'].emit("All experiments going in " + self.filemanager.name + " are finished.")
        
        
    def runTrial(self,params):
        Model.updateParameters(params)
        lightCurveData = Model.engine.makeLightCurve(params.quasarStartPos, params.quasarEndPos, params.extras.resolution)
        return lightCurveData
        
    