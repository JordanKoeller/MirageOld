'''
Created on Dec 26, 2017

@author: jkoeller
'''
from app.calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
from app.utility import NullSignal

from app.model import CalculationModel


class ExperimentTableRunner(object):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal):
        '''
        Constructor
        '''
        self.signals = signals

    def bindExperiments(self,experiments,filemanager):
        self.experimentQueue = experiments
        self.filemanager = filemanager

    def run(self):
        ctr = 0
        self.signals['progressLabel'].emit("Calculation starting ...")
        for params in self.experimentQueue:
            ctr += 1
            # self.signals['progressLabel'].emit("Experiment "+str(ctr-1)+" of "+len(self.experimentQueue) " finished.")
            numTrials = params.extras.numTrials 
            self.filemanager.newExperiment(params) #NEED TO IMPLIMENT
            exptRunner = ExperimentResultCalculator(params,self.signals)
            for expt in range(0,numTrials):
                newP = varyTrial(params,expt) #NEED TO IMPLIMENT
                model = CalculationModel(newP)
                model.bind_parameters()
                data = exptRunner.runExperiment(model) #NEED TO IMPLIMENT
                self.signals['progressLabel'].emit("Trial "+str(expt) +" of " + str(numTrials) + " from experiment " + str(ctr) +" of " + str(len(self.experimentQueue)) +" finished")
                self.filemanager.write(data)
            self.filemanager.closeExperiment()
        self.filemanager.flush()
        self.filemanager.close()
        self.signals['progressLabel'].emit("All experiments going in " + self.filemanager.prettyName + " are finished.")
