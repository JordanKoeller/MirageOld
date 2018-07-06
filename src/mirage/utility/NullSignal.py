'''
Created on Jun 9, 2017

@author: jkoeller
'''
import logging


class __NullSignal(object):
    '''
    classdocs
    '''
    counter = 0

    def __init__(self):
        '''
        Constructor
        '''
        pass

    
    def emit(self,*args,**kwargs):
        for i in args:
            if isinstance(i, str):
                logging.info(i)
    
    def connect(self,*args,**kwargs):
        pass
    
    def __getattr__(self,arg):
        pass
    def __getitem__(self,args):
        return self
    
NullSignal = __NullSignal()