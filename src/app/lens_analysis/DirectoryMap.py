'''
Created on Jun 8, 2017

@author: jkoeller
'''

import glob
import os

import numpy as np

from .Experiment import Experiment


class DirectoryMap(object):
    '''
    classdocs
    '''


    def __init__(self, dirname):
        '''
        Constructor
        '''
        self.__directory = dirname
        files = filter(os.path.isfile,glob.glob(self.__directory + "/*.dat"))
        self.__files = []
        for fille in files:
            self.__files.append(fille)
        self.__files.sort(key = lambda x: os.path.getmtime(x))
        self.__index = 0

    def __len__(self):
        return len(self.__files)
    
    @property
    def size(self):
        return len(self)
    
    @property
    def length(self):
        return len(self)
    
    def _getDataSet(self,trialNo,tableNo):
            self._fileobject.seek(self._lookupTable[trialNo,tableNo])
            return np.load(self._fileobject)

    @property
    def directory(self):
        return self.__directory
    
    
    @property
    def describe(self):
        print(str(self))
        
        
    def __str__(self):
        ret = ""
        for file in self.__files:
            ret += file
            ret += "\n"
        return ret
    
    def __getitem__(self,ind):
        if isinstance(ind,int):
            if ind < len(self.__files):
                return Experiment(self.__files[ind])
            else:
                raise IndexError("Index out of range.")
        elif ind in self.__files:
            return Experiment(self.__files[self.__files.index(ind)])
        else:
            raise IndexError("Invalid index of DirectoryMap instance. Index must be a number or filename.")
        
    def __iter__(self):
        return DirectoryMap(self.__directory)
    
    def __next__(self):
        if self.__index < self.size:
            try:
                ret = Experiment(self.__files[self.__index])
                self.__index += 1
                return ret
            except:
                self.__index = 0 
        else:
            self.__index = 0
            raise StopIteration
        
    