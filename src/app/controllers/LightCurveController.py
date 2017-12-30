'''
Created on Dec 20, 2017

@author: jkoeller
'''
from PyQt5.QtCore import pyqtSignal

from . import Controller

import numpy as np

class LightCurveController(Controller):
    '''
    Controller for managing a light curve. 
    '''
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()

    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        from app.views import PlotView
        self._viewType = PlotView
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal)
        self._x = np.arange(0,100,dtype=np.uint16)
        self._y = np.zeros(100,dtype=np.uint16)
        self._ind = 0
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType), "view must be a PlotView instance for LightCurveController to bind to it."
        self.signals['view_update_signal'].connect(view.update_slot)
        self.signals['destroy_view'].connect(view.destroy)

        
    def plot_xy(self,x,y):
        self.signals['view_update_signal'].emit({'xAxis':x,'yAxis':y})
        
    def add_point_and_plot(self,pixels):
        newY = pixels.size
        if self._ind == self._x.size:
            self.grow_array()
        self._y[self._ind] = newY
        self.plot_xy(self._x, self._y)
        self._ind += 1
        
    def grow_array(self):
        self._x = np.arange(0,self._x.size*2)
        self._y = np.append(self._y,np.zeros_like(self._y))
        
        
        
        
        