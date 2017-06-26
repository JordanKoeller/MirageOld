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


    def __init__(self, filepath, fileobject=None, params=None, lookuptable=[]):
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
        if lookuptable == []:
            self._lookupTable = np.load(self._fileobject)
        else:
            self._lookupTable = lookuptable
        self._exptTypes = {}
        for i in range(0,len(self._params.extras.desiredResults)):
            self._exptTypes[self._params.extras.desiredResults[i]] = i


    def _getDataSet(self,trialNo,tableNo):
            self._fileobject.seek(self._lookupTable[trialNo,tableNo])
            return np.load(self._fileobject)
    
    def prettyPath(self,filename):
        prettyString = filename
        while prettyString.partition('/')[2] != "":
            prettyString = prettyString.partition('/')[2]
        return prettyString
    
    def has(self,restype):
        return restype in self._exptTypes

    @property
    def file(self):
        return self._fileobject
    
    @property
    def filename(self):
        return self.prettyPath(self._filepath)
    
    @property
    def describe(self):
        print(str(self._exptTypes)+str(self))
        
    @property
    def parameters(self):
        return self._params
        
        
    def __str__(self):
        return str(self._params)

