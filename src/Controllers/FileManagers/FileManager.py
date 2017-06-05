'''
Created on Jun 3, 2017

@author: jkoeller
'''
from PyQt5 import QtCore, QtWidgets


class FileManager(QtCore.QThread):
    '''
    classdocs
    '''


    def __init__(self, signals):
        '''
        Constructor
        '''
        QtCore.QThread.__init__(self)
        self.signals = signals
        self.__hiddenWrite = self.write 
        
        
        
    def __getPretty(self,filename):
            prettyString = filename
            while prettyString.partition('/')[2] != "":
                prettyString = prettyString.partition('/')[2]
            return prettyString
        
    def fileReader(self,file):
        '''Abstract method to be implimented with how to load in the file'''
        
    def fileWriter(self,file,data):
        '''Abstract method to be implimented with what do do with data'''
        
    def write(self,data):
        """Method called by run, to get multithreaded support"""
        self.writeHelper(data)
        
    @property
    def fileextension(self):
        return ""
    
    @property
    def filetype(self):
        return ""
    def newFileChooser(self):
        return QtWidgets.QFileDialog.getSaveFileName(filter=self.fileextension)[0]

    def fileChooser(self):
        return QtWidgets.QFileDialog.getOpenFileName(filter=self.fileextension)[0]
    
    def read(self):
        filename = self.fileChooser()
        if filename:
            prettyString = self.__getPretty(filename)
            with open(filename, "r"+self.filetype) as file:
                ret = self.fileReader(file)
                self.signals['progressLabel'].emit(prettyString+" Loaded.")
                return ret
            
    def writeHelper(self,data):
        filename = self.newFileChooser()
        if filename:
            prettyString = self.__getPretty(filename)
            with open(filename, "w"+self.filetype) as file:
                self.fileWriter(file,data)
            self.signals['progressLabel'].emit(prettyString+" Saved.")
            
                
        
            
    def run(self, data):
        self.write(data)