'''
Created on Dec 22, 2017

@author: jkoeller
'''
from PyQt5.QtCore import pyqtSignal
import numpy as np

from . import Controller

from app.utility import Vector2D


class MagMapController(Controller):
    '''
    classdocs
    '''
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()
    _set_img = pyqtSignal(object)
    _set_ROI = pyqtSignal(object,object)
    
    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal,
                        set_ROI = self._set_ROI,
                        set_magmap = self._set_img)
        
    def bind_view_signals(self,view):
        self.signals['view_update_signal'].connect(view.update_slot)
        self.signals['destroy_view'].connect(view.destroy)
        self.signals['set_magmap'].connect(view.setMagMap)
        view.signals['ROI_set'].connect(self.setROI)
        self.signals['set_magmap'].emit(self._modelRef.magnification_map)
        
    def bind_to_model(self,modelRef):
        try:
            self._modelRef = modelRef
            logMap = np.log10(self._modelRef.magnification_map)
            print("Log of map")
            self.signals['set_magmap'].emit(logMap)
        except:
            print("Exception in binding magmapmodel")
        
    def setROI(self,start,end):
        print(type(start))
        vstart = Vector2D(start[0],start[1])
        vend = Vector2D(end[0],end[1])
        self._modelRef.specify_light_curve(vstart,vend)


