import numpy as np #type: ignore
import copy
import glob
import os
import sys

from .Experiment import Experiment

class DirectoryMap(object):
    '''
    Class for processing all the files in a directory at once. If the directory contains many file types, 
    will filter out all the files except those with the `.dat` extension. Allows for accessing files by filename, with syntax like that of a :class:`dict`
    or by numeric index. Files sorted numerically by time since the file was created, with newest last. Supports for loop comprehensions.

    Accessing a specific file automatically returns the file, decorated as a :class:`Experiment`.

    Parameters:
    dirname (:class:`str`): Directory to decorate. Relative to the current directory.
    '''


    def __init__(self, dirname:str):
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
        '''
        Number of `.dat` files in the directory.
        '''
        return len(self)
    
    @property
    def length(self):
        '''
        Alias of :func:`size`.
        '''
        return len(self)
    
    @property
    def directory(self):
        '''
        Returns the directory this :class:`DirectoryMap` decorates.
        '''
        return self.__directory
    
    
    @property
    def describe(self):
        '''
        Prints name of all the enclosed files.
        '''
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
