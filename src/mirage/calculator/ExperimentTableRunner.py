'''
Created on Dec 26, 2017

@author: jkoeller
'''
from mirage.calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
from mirage.utility import NullSignal



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
        from mirage.model import CalculationModel
        ctr = 0
        self.signals['progressLabel'].emit("Calculation starting ...")
        for params in self.experimentQueue:
            ctr += 1
            numTrials = params.extras.numTrials 
            self.filemanager.newExperiment(numTrials,len(params.extras.desiredResults)) #NEED TO IMPLIMENT
            exptRunner = ExperimentResultCalculator(params,self.signals)
            from datetime import datetime as DT
            for expt in range(0,numTrials):
                starttime = DT.now()
                newP = varyTrial(params,expt) #NEED TO IMPLIMENT
                model = CalculationModel(newP)
                model.bind_parameters()
                data = exptRunner.runExperiment(model,expt) #NEED TO IMPLIMENT
                self.signals['progressLabel'].emit("Trial "+str(expt) +" of " + str(numTrials) + " from experiment " + str(ctr) +" of " + str(len(self.experimentQueue)) +" finished")
                self.filemanager.write(data)
                endTime = DT.now()
                dSec = (endTime - starttime).seconds
                hrs = dSec // 3600
                mins = (dSec // 60) % 60
                secs = dSec % 60
                timeString = str(hrs)+" hours, " + str(mins) + " minutes, and " + str(secs) + " seconds"
                print("Experiment Finished in " + timeString)
            self.filemanager.closeExperiment(model.parameters)
        self.filemanager.close()
        self.signals['progressLabel'].emit("All experiments going in " + self.filemanager.prettyName + " are finished.")




# '''
# Created on Dec 26, 2017

# @author: jkoeller
# '''
# from mirage.calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
# from mirage.utility import NullSignal



# class ExperimentTableRunner(object):
#     '''
#     classdocs
#     '''


#     def __init__(self, signals = NullSignal):
#         '''
#         Constructor
#         '''
#         self.signals = signals

#     def bindExperiments(self,experiments,filemanager):
#         self.experimentQueue = experiments
#         self.filemanager = filemanager

#     def run(self):
#         from mirage.model import CalculationModel
#         ctr = -1
#         self.signals['progressLabel'].emit("Calculation starting ...")
#         relative_points = []
#         raw_model = CalculationModel(None)
#         for params in self.experimentQueue:
#             tmp_list = []
#             numTrials = params.extras.numTrials
#             for expt in range(0,numTrials):
#                 newP = varyTrial(params,expt)
#                 no_stars = newP.copy().clear_stars()
#                 raw_model.set_parameters(no_stars)
#                 raw_model.bind_parameters()
#                 rel_value = raw_model.get_raw_magnification()
#                 tmp_list.append(int(rel_value))
#             relative_points.append(tmp_list)
#         # del(raw_model)
#         for params in self.experimentQueue:
#             ctr += 1
#             # self.signals['progressLabel'].emit("Experiment "+str(ctr-1)+" of "+len(self.experimentQueue) " finished.")
#             numTrials = params.extras.numTrials 
#             self.filemanager.newExperiment(numTrials,len(params.extras.desiredResults)) #NEED TO IMPLIMENT
#             exptRunner = ExperimentResultCalculator(params,self.signals)
#             from datetime import datetime as DT
#             for expt in range(0,numTrials):
#                 starttime = DT.now()
#                 # del(newP)
#                 newP = varyTrial(params,expt) #NEED TO IMPLIMENT
#                 newP.setRawMag(relative_points[ctr][expt])
#                 model = CalculationModel(newP)
#                 model.bind_parameters()
#                 # raw_model.set_parameters(newP)
#                 # raw_model.bind_parameters()
#                 data = exptRunner.runExperiment(model,expt) #NEED TO IMPLIMENT
#                 self.filemanager.write(data)
#                 endTime = DT.now()
#                 dSec = (endTime - starttime).seconds
#                 hrs = dSec // 3600
#                 mins = (dSec // 60) % 60
#                 secs = dSec % 60
#                 timeString = str(hrs)+" hours, " + str(mins) + " minutes, and " + str(secs) + " seconds"
#                 print("Experiment Finished in " + timeString)
#             self.filemanager.closeExperiment(model.parameters)
#         self.filemanager.close()