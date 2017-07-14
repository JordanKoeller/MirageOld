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
    
    def connect(self,*args,**kwargs):
        pass
    
    def __getattr__(self,arg):
        pass
    def __getitem__(self,args):
        return self
    
NullSignal = __NullSignal()