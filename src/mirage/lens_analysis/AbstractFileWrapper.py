import numpy as np #type: ignore
import copy
import glob
import os
import sys

class AbstractFileWrapper(object):
    '''
    Abstract class, with methods for interracting with 'dat' files and directories containing them.
    Initialize AbstractFileWrapper object.
    
    Parameters:
    
    - `filepath`: (:class:`str`) path to file or directory of interest
    - `fileobject`: (file-like object) file object, if file is already opened. Default: :class:`None`
    - `params`: (:class:`Parameters`) Parameters object instance contained in the file. Passing in offers a slight optimization. Default: :class:`None`
    - `lookuptable` : (:class:`np.ndarray`) Array with byte shift for each data set present in the file. Passing in offers a slight optimization. Default: :class:`None`
     
    '''


    def __init__(self, filepath, fileobject=None, params=None, lookuptable=[]):
        '''
        '''
        self._filepath = filepath
        if not fileobject or not params:
            from mirage.io import ExperimentDataFileReader
            reader = ExperimentDataFileReader()
            reader.open(self._filepath)
            self._params, self._fileobject = reader.load()
            reader.close()
        else:
            self._fileobject = fileobject
            self._params = params
        if lookuptable == []:
            self._lookupTable = np.load(self._fileobject)
        else:
            self._lookupTable = lookuptable
        self._exptTypes = {}
        for i in range(0,len(self._params.extras.desiredResults)):
            self._exptTypes[self._params.extras.desiredResults[i]] = i


    def _getDataSet(self,trialNo,tableNo):
        '''
        Internal method for retrieving a specific data table from the file. Uses the passed in trialNo and tableNo as row and column indices for the lookup table.
        
        Offers a low-level way of getting a numpy array out of a `*.dat` file.
        
        
        Parameters:
        
        - `trialNo`: (`<int>`) Specify the trial number of interest.
        - `tableNo`: (`<int>`) Specify which data set collected by the experiment to report.
        
        Returns: :class:`<np.ndarray>`
        '''
        self._fileobject.seek(self._lookupTable[trialNo,tableNo])
        return np.load(self._fileobject)
    
    def prettyPath(self,filename):
        
        '''
        Prints the filename of the passed in string, removing the path and giving only the filename itself.
        
        Parameters:
        
        - 'filename': (:class:`str`) Filename to clean up and return.
        
        Returns: `str`
        '''
        prettyString = filename
        while prettyString.partition('/')[2] != "":
            prettyString = prettyString.partition('/')[2]
        return prettyString
    
    def has(self,restype):
        '''
        Return whether or not the experiment type specified by `restype` is represented in the data file.
        
        Returns: :class:'bool'
        '''
        return restype in self._exptTypes

    @property
    def file(self):
        '''
        Returns the file-like object this :class:`AbstractFileWrapper` decorates.
        '''
        return self._fileobject
    
    @property
    def filename(self):
        '''
        Returns the name of the file-like object this :class:`AbstractFileWrapper` decorates
        '''
        return self.prettyPath(self._filepath)
    
    @property
    def describe(self):
        '''
        Prints the system parameters along with a description of all the data enclosed within the file.
        '''
        print(str(self))
        
    @property
    def parameters(self):
        '''
        Returns an instance of the parameters specified by the file.
        '''
        return self._params
        
        
    def __str__(self):
        return str(self._params)
