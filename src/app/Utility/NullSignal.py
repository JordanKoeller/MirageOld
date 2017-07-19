'''
Created on Jun 9, 2017

@author: jkoeller
'''

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
                print(i)
            elif isinstance(i,int):
                self.counter += 1
                print("On step "  + str(self.counter))
    
    def connect(self,*args,**kwargs):
        pass
    
    def __getattr__(self,arg):
        pass
    def __getitem__(self,args):
        return self
    
NullSignal = __NullSignal()