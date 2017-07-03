'''
Created on Jun 1, 2017

@author: jkoeller
'''
import copy

from PyQt5 import QtCore

from Calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
from Models.Model import Model


class QueueThread(QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals):
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
            ctr += 1
            numTrials = params.extras.numTrials 
            self.filemanager.newExperiment(params) #NEED TO IMPLIMENT
            exptRunner = ExperimentResultCalculator(params,self.signals)
            tc = 0
            for expt in range(0,numTrials):
                self.signals['progressBar'].emit(tc)
                tc += 1
                self.signals['progressLabel'].emit("Processing trial "+str(tc) +" of " + str(numTrials) + " from experiment " + str(ctr) +" of " + str(len(self.experimentQueue)))
                print("Processing trial "+str(tc) +" of " + str(numTrials) + " from experiment " + str(ctr) +" of " + str(len(self.experimentQueue)))
                oldP = copy.deepcopy(Model.parameters)
                newP = varyTrial(params,tc) #NEED TO IMPLIMENT
                Model.updateParameters(newP)
                if oldP  and oldP.isSimilar(newP) == False:
                    Model.engine.reconfigure()
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
        
    