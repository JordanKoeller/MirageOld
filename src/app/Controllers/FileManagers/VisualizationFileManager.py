'''
Created on Jun 4, 2017

@author: jkoeller
'''
from PyQt5 import QtCore
import imageio

import numpy as np

from ...Utility.NullSignal import NullSignal
from .FileManager import FileManager


class VisualizationFileManager(FileManager,QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals=NullSignal):
        '''
        Constructor
        '''
        FileManager.__init__(self,signals)
        QtCore.QThread.__init__(self)
        self.__frames = []
        self.recording = False
        
    def fileReader(self, file):
        return None
    
    def giveFrame(self,frame):
        if self.recording:
            self.__frames.append(frame.copy())
            
    @property
    def fileextension(self):
        return "Movie (*.mp4)"

    @property
    def filetype(self):
        return ""

    def __asNPArray(self,im):
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

    def fileWriter(self,file,data = None):
        self.signals['progressBar'].emit("Rendering. Please Wait.")
        self.signals['progressBarMax'].emit(len(self.__frames))
        filename = file.name
        file.close()
        writer = imageio.get_writer(filename,fps=60)
        counter = 0
        for frame in self.__frames:
            img = self.__asNPArray(frame)
            writer.append_data(img)
            counter  += 1
            self.signals['progressBar'].emit(counter)
        writer.close()
        self.__frames = []
        self.signals['progressBar'].emit(0)
        
    def write(self, data = None):
        if self.recording:
            self.run()
            self.recording = False
            
    def cancelRecording(self):
        self.recording = False
        self.__frames = []
            
    def run(self):
        self.writeHelper(None)