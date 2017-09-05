'''
Created on Jun 1, 2017

@author: jkoeller
'''

from PyQt5 import QtCore

from ...Calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
from ...Models.Model import Model
from ...Utility.NullSignal import NullSignal


class QueueThread(QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal):
        '''
        Constructor
        '''
        QtCore.QThread.__init__(self)
        self.signals = signals

    def bindExperiments(self,experiments,filemanager):
        self.experimentQueue = experiments
        self.filemanager = filemanager

    def run(self):
        ctr = 0
        for params in self.experimentQueue:
            print(params.galaxy.stars)
            ctr += 1
            numTrials = params.extras.numTrials 
            self.filemanager.newExperiment(params) #NEED TO IMPLIMENT
            exptRunner = ExperimentResultCalculator(params,self.signals)
            for expt in range(0,numTrials):
                self.signals['progressBar'].emit(expt+1)
                self.signals['progressLabel'].emit("Processing trial "+str(expt+1) +" of " + str(numTrials) + " from experiment " + str(ctr) +" of " + str(len(self.experimentQueue)))
                newP = varyTrial(params,expt+1) #NEED TO IMPLIMENT
                Model.updateParameters(newP)
                data = exptRunner.runExperiment() #NEED TO IMPLIMENT
                self.filemanager.sendTrial(data)
            self.filemanager.closeExperiment()
        self.filemanager.flush()
        self.filemanager.close()
        self.signals['progressLabel'].emit("All experiments going in " + self.filemanager.prettyName + " are finished.")
        
        
    def runTrial(self,params):
        Model.updateParameters(params)
        lightCurveData = Model.engine.makeLightCurve(params.quasarStartPos, params.quasarEndPos, params.extras.resolution)
        return lightCurveData
        
    