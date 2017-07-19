'''
Created on Jun 5, 2017

@author: jkoeller
'''

from PyQt5 import QtCore, QtWidgets

from .ParametersFileManager import ParametersFileManager
from .FileManager import FileManager
import numpy as np
from ...Utility.NullSignal import NullSignal


class QueueFileManager(FileManager,QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal,directory=None):
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
        if not directory:
            directory = self.getDirectory()
        self.directory = directory
        self.__name = directory
        
    @property
    def fileextension(self):
        return "DataFile (*.dat)"
    
    @property
    def filetype(self):
        return "b+"

    def getDirectory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory()
        return directory
    
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
        for i in range(0,len(data)):
            self.dataSizeArray[self.trialCount,i] = self.exptFile.tell()
            np.save(self.exptFile,data[i])
        self.trialCount += 1
        self.signals['progressBar'].emit(self.trialCount)

    def getPretty(self,filename):
            prettyString = filename
            while prettyString.partition('/')[2] != "":
                prettyString = prettyString.partition('/')[2]
            return prettyString
        
    @property
    def name(self):
        return self.__name
    
    @property
    def prettyName(self):
        return self.getPretty(self.name)
    
    @property
    def madeDirectory(self):
        if self.directory:
            return True
        else:
            return False
        
    def run(self,data):
        '''
            Data is a tuple, containing references to numpy arrays. Index of tuple directly correlates to the index of the dataSizeArray to insert it into.
        '''
        pass
    
    def __del__(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()
            
        