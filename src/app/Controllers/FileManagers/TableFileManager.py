'''
Created on Jun 3, 2017

@author: jkoeller
'''
import pickle

from .FileManager import FileManager
from ...Utility.NullSignal import NullSignal


class TableFileManager(FileManager):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal):
        '''
        Constructor
        '''
        FileManager.__init__(self,signals)
        
    def fileReader(self, file):
        return pickle.load(file)

    def fileWriter(self, file, data):
        pickle.dump(data,file)
                
    @property
    def fileextension(self):
        return "Parameters (*.params)"
    
    @property
    def filetype(self):
        return "b+"