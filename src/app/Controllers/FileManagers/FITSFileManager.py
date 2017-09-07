'''
Created on Jun 4, 2017

@author: jkoeller
'''
from astropy.io import fits

from ...Utility.NullSignal import NullSignal
from .FileManager import FileManager


class FITSFileManager(FileManager):
    '''
    classdocs
    '''


    def __init__(self, signals = NullSignal):
        '''
        Constructor
        '''
        FileManager.__init__(self,signals)
        
        
    def fileReader(self, file):
        return None

    def fileWriter(self, file, data):
        filename = file.name
        file.close()
        fits.writeto(filename,data)
        
        
    @property
    def fileextension(self):
        return "FITS (*.fits)"