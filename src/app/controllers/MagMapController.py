'''
Created on Dec 22, 2017

@author: jkoeller
'''
from PyQt5.QtCore import pyqtSignal

from . import Controller


class MagMapController(Controller):
    '''
    classdocs
    '''
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()

    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal)
