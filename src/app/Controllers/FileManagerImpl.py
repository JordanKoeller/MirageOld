'''
Created on Jul 28, 2017

@author: jkoeller
'''

import pickle

import imageio

from app import Preferences
from app.Utility import asynchronous

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


    def __init__(self):
        '''
        Constructor
        '''
        FileWriter.__init__(self)
        
    def open(self, filename=None):
        FileWriter.open(self, filename)
        self._file = open(self._filename,'wb+')
        
    def write(self, data):
        pickle.dump(data,self._file)

    def close(self):
        self._file.close()
        self._file = None
        
    @property
    def _fileextension(self):
        return '.params'
    

class TableFileManager(FileWriter):
    
    def __init__(self):
        FileWriter.__init__(self)
        self._parametersFileManager = ParametersFileManager()
        
    def open(self, filename=None):
        self._parametersFileManager.open(filename)
        
    def write(self,data):
        for i in data:
            self._parametersFileManager.write(i)
        
    def close(self):
        self._parametersFileManager.close()
        
        
    @property
    def _fileextension(self):
        return '.params'
    
class ModelFileManager(FileReader):
    """class for reading model configurations. Can accept .dat, .param, and .params files and parse to a model"""
    def __init__(self):
        super(ModelFileManager, self).__init__()
        
    @property
    def _fileextension(self):
        return '.param'