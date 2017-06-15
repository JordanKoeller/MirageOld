'''
Created on Jun 12, 2017

@author: jkoeller
'''

from Controllers.ParameterInputParser.ParameterInputParser import ParameterInputParser
from Utility.NullSignal import NullSignal


class ArcsecParameterInputParser(ParameterInputParser):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        ParameterInputParser.__init__(self)
        self._inputUnit = 'arcsec'
        
    def parse(self, view, errorSigna=NullSignall):