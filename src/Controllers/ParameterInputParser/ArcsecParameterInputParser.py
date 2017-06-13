'''
Created on Jun 12, 2017

@author: jkoeller
'''

from Controllers.ParameterInputParser.ParameterInputParser import ParameterInputParser


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
        
    def parse(self, view, errorSignal):