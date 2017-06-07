'''
Created on Jun 5, 2017

@author: jkoeller
'''

from PyQt5 import QtCore, QtWidgets

from Controllers.FileManagers import ParametersFileManager
from Controllers.FileManagers.FileManager import FileManager
import numpy as np


class QueueFileManager(FileManager,QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals):
        '''
        Constructor
        '''
        FileManager.__init__(self, signals)
        QtCore.QThread.__init__(self)
        self.signals = signals
        self.__paramsFileManager = ParametersFileManager(signals)
        self.exptFile = None
        self.pickledParams = None
        self.dataSizeArray = None
        self.dataSizeLoc = None
        self.trialCount = 0
        self.experimentCount = 0 #Specifies which row in the table to be written next
        
    @property
    def fileextension(self):
        return "DataFile (*.dat)"
    
    @property
    def filetype(self):
        return "b+"

    def getDirectory(self):
        self.directory = QtWidgets.QFileDialog.getExistingDirectory()
        self.__name = self.directory
        return self.directory
    
    def newExperiment(self,params):
        name = params.extras.name
        filename = self.directory+"/"+name+".dat"
        self.exptFile = open(filename,'wb+')
        self.dataSizeArray = self.getDataSizeArray(params)
        self.__paramsFileManager.fileWriter(self.exptFile,params)
        self.signals['progressLabel'].emit("Processing "+self.getPretty(filename))
        self.signals['progressBarMax'].emit(params.extras.numTrials)
        self.dataSizeLoc = self.exptFile.tell()
        self.trialCount = 0 #Trial number to be written next. Important because it is the index used for indexing into the dataSizeArray to specify the size of the data for that trial.
        np.save(self.exptFile,self.dataSizeArray)
        
    def closeExperiment(self):
        self.exptFile.flush()
        tmploc = self.exptFile.tell()
        self.exptFile.seek(self.dataSizeLoc,0)
        np.save(self.exptFile,self.dataSizeArray)
        #Stream cleanup
        self.exptFile.flush()
        self.exptFile.seek(tmploc,0)
        self.exptFile.flush()
        self.exptFile.close()
        #Class data cleanup
        self.exptFile = None
        self.pickledParams = None
        self.dataSizeArray = None
        self.dataSizeLoc = None
        self.trialCount = 0
        self.experimentCount += 1
        
    def flush(self):
        if self.exptFile:
            self.exptFile.flush()
            
    def close(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()
        self.signals['progressBar'].emit(0)
    
    
    def getDataSizeArray(self,params):
        numtrials = params.extras.numTrials
        numDataPoints = len(params.extras.desiredResults)
        ret = np.zeros((numtrials,numDataPoints),dtype=np.int64)
        return ret
    
    def sendTrial(self, data):
        self.run(data)
        
    @property
    def name(self):
        return self.__name
        
    def run(self,data):
        '''
            Data is a tuple, containing references to numpy arrays. Index of tuple directly correlates to the index of the dataSizeArray to insert it into.
        '''
        for i in range(0,len(data)):
            self.dataSizeArray[self.trialCount,i] = self.exptFile.tell()
            np.save(self.exptFile,data[i])
        self.trialCount += 1
        self.signals['progressBar'].emit(self.trialCount)
        
    def __del__(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()
            
        
