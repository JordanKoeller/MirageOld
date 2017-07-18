from PIL import Image
from PyQt5 import QtCore
import imageio

import numpy as np

from ...Utility.NullSignal import NullSignal
from .FileManager import FileManager


class MediaFileManager(FileManager,QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal):
        '''
        Constructor
        '''
        FileManager.__init__(self,signals)
        QtCore.QThread.__init__(self)
        self.__frames = []
        self.framerate = 25
        
    def fileReader(self, file):
        return Image.open(file.name)
    
    def sendFrame(self,frame):
        #Frame is of type pixmap
        self.__frames.append(frame.copy())
        
    def __asNPArray(self,im):
        im = im.toImage()
        im = im.convertToFormat(4)
        width = im.width()
        height = im.height()
        ptr = im.bits()
        ptr.setsize(im.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        return arr
        
    def fileWriter(self,file,data = None):
        self.signals['progressBar'].emit("Rendering. Please Wait.")
        if 'progressBarMax' in self.signals:
            self.signals['progressBarMax'].emit(len(self.__frames))
        filename = file.name
        file.close()
        writer = imageio.get_writer(filename,fps=self.framerate)
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
        self.run()
            
    def cancelRecording(self):
        self.__frames = []
        
    def run(self):
        self.writeHelper(None)
        
    @property
    def fileextension(self):
        return ""