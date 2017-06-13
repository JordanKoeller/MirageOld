'''
Created on Jun 12, 2017

@author: jkoeller
'''
from Controllers.ParameterInputParser.ParameterInputParser import ParameterInputParser


class RgParameterInputParser(ParameterInputParser):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        ParameterInputParser.__init__(self)
        
    def parse(self, view, errorSignal):
        self._inputUnit = 'arcsec'
        param1 = ParameterInputParser.parse(self, view, errorSignal)
        rg = u.Quanity(param1.quasarRadius_rg
        