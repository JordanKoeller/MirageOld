'''
Created on Jun 9, 2017

@author: jkoeller
'''
import logging
logging.basicConfig(filename='progress.log',level=logging.INFO)


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
                pass
                # print(i)
                # logging.info(i)
            elif isinstance(i,int):
                # print(i)
                self.counter += 1
                logging.info("On step "+str(self.counter))
#                 print("On step "  + str(self.counter))
    
    def connect(self,*args,**kwargs):
        pass
    
    def __getattr__(self,arg):
        pass
    def __getitem__(self,args):
        return self
    
NullSignal = __NullSignal()