'''
Created on Jun 1, 2017

@author: jkoeller
'''

from PyQt5 import QtCore
from ...Calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
from app.Models import Model
from ...Utility.NullSignal import NullSignal
from ...Utility import asynchronous

class QueueThread(object):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal):
        '''
        Constructor
        '''
        # QtCore.QThread.__init__(self)
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
                print("Done trial")
                Model.updateModel('default',newP)
                print("Done update")
                data = exptRunner.runExperiment() #NEED TO IMPLIMENT
                print("Done expt")
                self.filemanager.sendTrial(data)
                print("Finished Trial")
            self.filemanager.closeExperiment()
        self.filemanager.flush()
        self.filemanager.close()
        self.signals['progressLabel'].emit("All experiments going in " + self.filemanager.prettyName + " are finished.")
        
        
    def runTrial(self,params):
        ModelImpl.updateParameters(params)
        lightCurveData = ModelImpl.engine.makeLightCurve(params.quasarStartPos, params.quasarEndPos, params.extras.resolution)
        return lightCurveData
        
    