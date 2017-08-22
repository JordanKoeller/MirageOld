'''
Created on Jul 28, 2017

@author: jkoeller
'''

import pickle
import json

import imageio

from app import Preferences
from app.Utility import asynchronous

from ..Models.ModelImpl import ModelImpl
from app.Parameters import Parameters
from .FileManager import FileWriter, FileReader


class RecordingFileManager(FileWriter):
    
    def __init__(self,buffer_frames=False):
        FileWriter.__init__(self)
        self._bufferFrames = buffer_frames
        
    def open(self, filename=None, *args, **kwargs):
        FileWriter.open(self, filename=filename, *args, **kwargs)
        self._writer = imageio.get_writer(self._filename,fps=Preferences.framerate)
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
        object.__init__(self,*args,**kwargs)

    def open(self, filename=None):
        FileWriter.open(self, filename)
        if self._filename:
            self._file = open(self._filename,'w+')
        
    def write(self, data):
        self._file.write(data.jsonString)

    def close(self):
        self._file.close()
        self._file = None
        
    @property
    def _fileextension(self):
        return '.params'
    

class TableFileWriter(FileWriter):
    
    def __init__(self):
        FileWriter.__init__(self)
        
    def open(self, filename=None):
        FileWriter.open(self,filename)

    def write(self,data):
        if self._filename:
            self._file = open(self._filename,'wb+')
            pickle.dump(data,self._file)
        
    def close(self):
        pass        
        
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
            self._file = open(self._filename,'rb+')
            return pickle.load(self._file)
        
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
            self._file = open(self._filename,'rb+')
            model = pickle.load(self._file)
            if isinstance(model,Parameters):
                model = ModelImpl(model)
            elif isinstance(model,ModelImpl):
                pass
            else:
                raise IOError("Specified file does not contain a model.")
            return model
        else: return None

    @property
    def _fileextension(self):
        return '.param'

class ModelFileWriter(FileWriter):
    """class for reading model configurations. Can accept .dat, .param, and .params files and parse to a model"""
    def __init__(self):
        super(ModelFileWriter, self).__init__()
        
    @property
    def _fileextension(self):
        return '.param'

    def write(self,data):
        if self._filename:
            self._file = open(self._filename,'wb+')
            pickle.dump(data,self._file)
        else:
            self.open()
            self.write(data)

