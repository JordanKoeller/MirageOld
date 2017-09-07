'''
Created on Jul 25, 2017

@author: jkoeller
'''

from .Controller import Controller


class MasterController(Controller):
    '''
    extends Controller

    
    Top - level controller. Alone, this controller does nothing, other than accept signals emitted by startSignal.

    When supplied with delegates, MasterController will call calculate() on all its children, and have all its children call
    calculate on their children, until no children remain.
    '''


    def __init__(self,startSignal=None):
        '''
        Constructor

        args:
        startSignal (QtCore.pyqtSignal) signal that when emitted, will cause this controller to calculate.
        '''
        Controller.__init__(self)
        if startSignal:
	        self.startSignal = startSignal
	        self.startSignal.connect(self.run)
	        self.run()
        # self._children = delegates
                