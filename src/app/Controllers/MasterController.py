'''
Created on Jul 25, 2017

@author: jkoeller
'''

from .Controller import Controller


class MasterController(Controller):
    '''
    classdocs
    '''


    def __init__(self,startSignal=None):
        '''
        Constructor
        '''
        Controller.__init__(self)
        if startSignal:
	        self.startSignal = startSignal
	        self.startSignal.connect(self.run)
	        self.run()
        # self._children = delegates
                