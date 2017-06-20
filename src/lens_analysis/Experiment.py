'''
Created on Jun 7, 2017

@author: jkoeller
'''

import pickle

from lens_analysis.AbstractFileWrapper import AbstractFileWrapper
from lens_analysis.Trial import Trial


class Experiment(AbstractFileWrapper):
    '''
    classdocs
    '''


    def __init__(self, filepath, fileobject=None,params=None,lookuptable=[]):
        '''
        Constructor
        '''
        AbstractFileWrapper.__init__(self,filepath,fileobject,params,lookuptable)
        self.__index = 0
        

    @property
    def regenerate(self):
        return Experiment(self._filepath)

    
    def __next__(self):
        if self.__index < len(self._lookupTable):
            ret =  Trial(self._filepath,self.__index,self._fileobject,self._params,self._lookupTable)
            self.__index += 1
            return ret 
        else:
            self.__index = 0
            raise StopIteration
            
    def __getitem__(self,ind):
        if isinstance(ind,int):
            if ind < len(self._lookupTable):
                return Trial(self._filepath,ind,self._fileobject,self._params,self._lookupTable)
            else:
                raise IndexError("Index out of range.")
        else:
            raise ValueError("Index must be of type int")

    def __len__(self):
        return len(self._lookupTable)
        



    @property
    def size(self):
        return len(self)
    
    @property
    def length(self):
        return len(self)
        
        
    def exportParameters(self,filename):
        file = open(filename,'wb+')
        pickle.dump(self._params,file)
        
    
    def __iter__(self):
        return Experiment(self._filepath,self._fileobject,self._params,self._lookupTable)
        

