'''
Created on Jul 17, 2017

@author: jkoeller
'''

class SignalRepo(object):
    '''
    classdocs
    '''

    __signals = {}

    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        pass
        
        
    def removeSignals(self,args):
        for i in args:
            self.__signals.pop(i)
        
    @property
    def signals(self):
        return self.__signals
    
    def addSignals(self,**kwargs):
        self.__signals.update(kwargs)