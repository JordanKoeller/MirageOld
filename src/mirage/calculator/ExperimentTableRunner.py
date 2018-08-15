'''
Created on Dec 26, 2017

@author: jkoeller
'''
from datetime import datetime as DT


from mirage.calculator.ExperimentResultCalculator import ExperimentResultCalculator, varyTrial
from mirage.utility import NullSignal



class ExperimentTableRunner(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass

    # def bindExperiments(self,simulation,filemanager):
    #     self.experimentQueue = simulations
    #     self.filemanager = filemanager

    # def run(self):
    #     from mirage.model import CalculationModel
    #     ctr = 0
    #     for simulation in self.experimentQueue:
    #         params = simulation.parameters
    #         expts = simulation.experiments
    #         ctr += 1
    #         numTrials = expts.num_trials
    #         self.filemanager.newExperiment(numTrials,len(expts.desired_results)) #NEED TO IMPLIMENT
    #         exptRunner = ExperimentResultCalculator(simulation)
    #         for expt in range(0,numTrials):
    #             starttime = DT.now()
    #             new_sim = varyTrial(simulation,expt) #NEED TO IMPLIMENT
    #             model = CalculationModel(new_sim)
    #             model.bind_simulation()
    #             data = exptRunner.run_experiment(model,expt) #NEED TO IMPLIMENT
    #             self.filemanager.write(data)
    #             endTime = DT.now()
    #             dSec = (endTime - starttime).seconds
    #             hrs = dSec // 3600
    #             mins = (dSec // 60) % 60
    #             secs = dSec % 60
    #             timeString = str(hrs)+" hours, " + str(mins) + " minutes, and " + str(secs) + " seconds"
    #             print("Experiment Finished in " + timeString)
    #         self.filemanager.closeExperiment(simulation)
    #     self.filemanager.close()

    def run(self,simulation,filemanager):
        from mirage.model import CalculationModel
        expts = simulation.experiments
        num_trials = expts.num_trials
        filemanager.new_experiment(num_trials,len(expts))
        exptRunner = ExperimentResultCalculator(simulation)
        calculation_model = CalculationModel(simulation)
        for expt in range(0,num_trials):
            starttime = DT.now()
            new_sim = varyTrial(simulation,expt)
            calculation_model.set_simulation(new_sim)
            calculation_model.bind_simulation()
            data = exptRunner.run_experiment(calculation_model)
            filemanager.write(data)
            endTime = DT.now()
            dSec = (endTime - starttime).seconds
            hrs = dSec // 3600
            mins = (dSec // 60) % 60
            secs = dSec % 60
            timeString = str(hrs)+" hours, " + str(mins) + " minutes, and " + str(secs) + " seconds"
            print("Experiment Finished in " + timeString)
        filemanager.close_experiment(simulation)
        filemanager.close()



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