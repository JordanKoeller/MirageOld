'''
Created on Jun 7, 2017

@author: jkoeller
'''
import pickle

import numpy as np


class AbstractFileWrapper(object):
    '''
    classdocs
    '''


    def __init__(self, filepath, fileobject=None, params=None, lookuptable=None):
        '''
        Constructor
        '''
        self._filepath = filepath
        if not fileobject:
            self._fileobject = open(filepath, 'rb')
        else:
            self._fileobject = fileobject
        if not params:
            try:
                self._params = pickle.load(self._fileobject)
            except ImportError:
                self._params = pickle.load(self._fileobject)
        else:
            self._params = params
        if not lookuptable:
            self._lookupTable = np.load(self._fileobject)
        else:
            self._lookupTable = lookuptable
        self._exptTypes = self._params.extras.desiredResults


    def getDataSet(self,trialNo,tableNo):
            self._fileobject.seek(self._lookupTable[trialNo,tableNo])
            return np.load(self._fileobject)

    @property
    def file(self):
        return self._fileobject
    
    
    @property
    def describe(self):
        print(str(self))
        
    @property
    def parameters(self):
        return self._params
        
        
    def __str__(self):
        return str(self._params)

