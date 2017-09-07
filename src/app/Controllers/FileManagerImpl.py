'''
Created on Jul 28, 2017

@author: jkoeller
'''

import imageio
import json
import numpy as np

from app.Preferences import GlobalPreferences
from app.Utility import asynchronous

from .FileManager import FileWriter, FileReader


def _formatJson(data):
    ret = json.dumps(data,indent=4)
    return ret

class RecordingFileManager(FileWriter):
    
    def __init__(self,buffer_frames=False):
        FileWriter.__init__(self)
        self._bufferFrames = buffer_frames
        
    def _asNPArray(self,im):
        im = im.toImage()
        im = im.convertToFormat(4)
        width = im.width()
        height = im.height()
        ptr = im.bits()
        ptr.setsize(im.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        arr2 = arr.copy()
        arr[:,0] = arr2[:,2]
        arr[:,2] = arr2[:,0]
        return arr
        
    def open(self, filename=None, *args, **kwargs):
        FileWriter.open(self, filename=filename, *args, **kwargs)
        self._writer = imageio.get_writer(self._filename,fps=GlobalPreferences['max_frame_rate'])
        self._frames = []
    
    def write(self, frame):
        if self._bufferFrames:
            self._frames.append(frame)
        else:
            frame = self._asNPArray(frame)
            self._writer.append_data(frame)
            
    @property
    def _fileextension(self):
        return '.mp4'
            
    @asynchronous
    def close(self):
        print("File saved")
        if self._bufferFrames:
            for frame in self._frames:
                img = self._asNPArray(frame)
                self._writer.appendData(img)
            self._frames = []
        self._writer.close()


class ParametersFileManager(FileWriter):
    '''
    classdocs
    '''

    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        FileWriter.__init__(self)

    def open(self, filename=None):
        FileWriter.open(self, filename)
        if self._filename:
            self._file = open(self._filename,'w+')
        
    def write(self, data):
        jsonString = _formatJson(data.jsonString)
        self._file.write(jsonString)

    def close(self):
        self._file.close()
        self._file = None
        
    @property
    def _fileextension(self):
        return '.param'

class ParametersFileReader(FileReader):

    def __init__(self,*args,**kwargs):
        FileReader.__init__(self,*args,**kwargs)

    def open(self, filename=None):
        FileReader.open(self,filename)

    def load(self):
        self._filename = self._filename or self.open()
        from ..Parameters.Parameters import ParametersJSONDecoder
        self._file = open(self._filename)
        model = json.load(self._file)
        decoder = ParametersJSONDecoder()
        model = decoder.decode(model)
        return model

    def close(self):
        self._file.close()
    

class TableFileWriter(FileWriter):
    
    def __init__(self):
        FileWriter.__init__(self)
        
    def open(self, filename=None):
        FileWriter.open(self,filename)

    def write(self,data):
        if self._filename:
            self._file = open(self._filename,'wb+')
            dataStrings = []
            for i in data:
                dataStrings.append(i.jsonString)
            js = _formatJson(dataStrings)
            self._file.write(bytes(js,'utf-8'))
        
    def close(self):
        self._file.close()
        
    @property
    def _fileextension(self):
        return '.params'
    
class TableFileReader(FileReader):
    
    def __init__(self):
        FileWriter.__init__(self)
        
    def open(self, filename=None):
        FileWriter.open(self,filename)

    def load(self):
        if self._filename:
            from ..Parameters.Parameters import ParametersJSONDecoder
            decoder = ParametersJSONDecoder()
            self._file = open(self._filename,'rb+')
            data = self._file.read()
            paramList = json.loads(data)
            ret = []
            for p in paramList:
                ret.append(decoder.decode(p))
            return ret
        
    def close(self):
        pass        
        
    @property
    def _fileextension(self):
        return '.params'

class ModelFileReader(FileReader):
    """class for reading model configurations. Can accept .dat, .param, and .params files and parse to a model"""
    def __init__(self):
        super(ModelFileReader, self).__init__()
        

    def load(self,filename=None,*args,**kwargs):
        if self._filename:
            from ..Parameters.Parameters import ParametersJSONDecoder
            self._file = open(self._filename)
            model = json.load(self._file)
            decoder = ParametersJSONDecoder()
            model = decoder.decode(model)
            if model:
                from ..Models.ModelImpl import ModelImpl
                model = ModelImpl(model)
            else:
                raise IOError("Specified file does not contain a model.")
            return model
        else: return None

    @property
    def _fileextension(self):
        return '.param'

# class ModelFileWriter(FileWriter):
#     """class for reading model configurations. Can accept .dat, .param, and .params files and parse to a model"""
#     def __init__(self):
#         super(ModelFileWriter, self).__init__()
        
#     @property
#     def _fileextension(self):
#         return '.param'

#     def write(self,data):
#         if self._filename:
#             self._file = open(self._filename,'wb+')
#             pickle.dump(data,self._file)
#         else:
#             self.open()
#             self.write(data)

class ExperimentDataFileWriter(FileWriter):
    """docstring for ExperimentDataFileWriter"""
    def __init__(self):
        super(ExperimentDataFileWriter, self).__init__()
        
    def open(self,filename=None):
        self._directory = filename or self.getDirectory()
        self.exptFile = None
        self.pickledParams = None
        self.dataSizeArray = None
        self.dataSizeLoc = None
        self.trialCount = 0
        self.experimentCount = 0 #Specifies which row in the table to be written next
        self._name = self._directory
        self._parametersWriter = ParametersFileManager()

    def getDirectory(self):
        from PyQt5 import QtWidgets
        directory = QtWidgets.QFileDialog.getExistingDirectory()
        return directory

    def newExperiment(self,params):
        name = params.extras.name
        filename = self.directory+'/'+name+'.dat'
        self.exptFile = open(filename,'wb+')
        self.dataSizeArray = self.getDataSizeArray(params) #TODO
        jsonString = _formatJson(params.jsonString)
        self.exptFile.write(bytes(jsonString,'utf-8'))
        self.exptFile.write(b'\x93')
        self.parametersEndLoc = self.exptFile.tell()
        self.trialCount = 0
        np.save(self.exptFile,self.dataSizeArray)

    def closeExperiment(self):
        self.exptFile.flush()
        tmploc = self.exptFile.tell()
        self.exptFile.seek(self.parametersEndLoc,0)
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

    def getDataSizeArray(self,params):
        numtrials = params.extras.numTrials
        numDataPoints = len(params.extras.desiredResults)
        ret = np.zeros((numtrials,numDataPoints),dtype=np.int64)
        return ret

    def write(self,data):
        for i in range(0,len(data)):
            self.dataSizeArray[self.trialCount,i] = self.exptFile.tell() - self.parametersEndLoc
            np.save(self.exptFile,data[i])
        self.trialCount += 1

    def getPretty(self,string):
        prettyString = string
        divisions = prettyString.split('/')
        last = divisions[len(divisions)-1]
        return last

    def flush(self):
        if self.exptFile:
            self.exptFile.flush()
            
    def close(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()

    @property
    def _fileextension(self):
        return '.dat'

    @property
    def name(self):
        return self._name 
    
    @property
    def directory(self):
        return self._directory

    @property
    def prettyName(self):
        return self.getPretty(self.name)

    def __del__(self):
        if self.exptFile:
            self.exptFile.flush()
            self.exptFile.close()
            
        
class ExperimentDataFileReader(FileReader):


    def __init__(self):
        FileReader.__init__(self)

    def open(self,filename=None):
        self._filename = filename or self.getFile()

    def load(self):
        with open(self._filename,'rb+') as file:
            import tempfile
            from ..Parameters.Parameters import ParametersJSONDecoder
            paramsJSON, data = file.read().split(b'\x93',maxsplit=1)
            dataFile = tempfile.TemporaryFile()
            dataFile.write(data)
            decoder = ParametersJSONDecoder()
            paramsDict = json.loads(paramsJSON)
            params = decoder.decode(paramsDict)
            dataFile.seek(0)
            return (params,dataFile)

    def close(self):
        pass