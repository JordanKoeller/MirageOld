'''
Created on Jun 7, 2017

@author: jkoeller
'''
import pickle

import numpy as np


class __Experiment(object):
    '''
    classdocs
    '''


    def __init__(self, filepath):
        '''
        Constructor
        '''
        self.__filepath = filepath
        self.__fileobject = open(filepath,'rb')
        try:
            self.__params = pickle.load(self.__fileobject)
        except ImportError:
            self.__params = pickle.load(self.__fileobject)
        self.__exptTypes = self.__params.extras.desiredResults
        self.__lookupTable = np.load(self.__fileobject)