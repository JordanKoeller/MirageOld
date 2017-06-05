'''
Created on Jun 1, 2017

@author: jkoeller
'''
from PyQt5 import QtCore

from Models import Model


class QueueThread(QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals):
        '''
        Constructor
        '''
        
    def run(self, experimentQueue,filemanager):
        for expt in experimentQueue:
            params = expt.parameters
            name = expt.name
            desc = expt.desc
            numTrials = expt.trials 
            filemanager.newExperiment(name,params,desc) #NEED TO IMPLIMENT
            for expt in range(0,numTrials):
                params = expt.varyTrial(params) #NEED TO IMPLIMENT
                data = expt.runTrial(params) #NEED TO IMPLIMENT
                filemanager.sendTrial(data) #NEED TO IMPLIMENT
            filemanager.closeExperiment()  #NEED TO IMPLIMENT
        filemanager.flush()
        filemanager.close()
        
    def runTrial(self,params):
        Model.updateParameters(params)
        lightCurveData = Model.engine.makeLightCurve(params.quasarStartPos, params.quasarEndPos, params.extras.resolution)
        return lightCurveData
        
    