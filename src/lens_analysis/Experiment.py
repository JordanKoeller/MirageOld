'''
Created on Jun 7, 2017

@author: jkoeller
'''

import pickle

from Models.Parameters.ExperimentParams import ResultTypes
from lens_analysis.AbstractFileWrapper import AbstractFileWrapper
from lens_analysis.Trial import Trial


class Experiment(AbstractFileWrapper):
    '''
    classdocs
    '''


    def __init__(self, filepath, fileobject=None,params=None,lookuptable=None):
        '''
        Constructor
        '''
        AbstractFileWrapper.__init__(self,filepath,fileobject,params,lookuptable)
        self.__index = 0
        
        

    
    
    @property
    def lightcurves(self):
        if ResultTypes.MAGMAP in self._exptTypes:
            pass ###WILL NEED TO FILL IN A WAY TO GET BACK TYPE
        else:
            raise AttributeError("No light curve data present in this experiment")
    
        
    @property
    def magmaps(self):
        if ResultTypes.LIGHT_CURVE in self._exptTypes:
            pass ###WILL NEED TO FILL IN A WAY TO GET BACK TYPE
        else:
            raise AttributeError("No magnification map data present in this experiment")        
        

    @property
    def starfields(self):
        if ResultTypes.STARFIELD in self._exptTypes:
            pass ###WILL NEED TO FILL IN A WAY TO GET BACK TYPE
        else:
            raise AttributeError("No star field data present in this experiment")        


    
    def __next__(self):
        if self.index < len(self._lookuptable):
            ret =  Trial(self._filepath,self.__index,self._fileobject,self._params,self._lookupTable)
            self.__index += 1
            return ret 
        else:
            return StopIteration
        
    def exportParameters(self,filename):
        file = open(filename,'wb+')
        pickle.dump(self._params,file)
        
    
    def __iter__(self):
        return self
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    
        