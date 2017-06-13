'''
Created on Jun 9, 2017

@author: jkoeller
'''

class __NullSignal(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass

    
    def emit(self,*args,**kwargs):
        pass
    
NullSignal = __NullSignal()