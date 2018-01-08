'''
Created on Dec 22, 2017

@author: jkoeller
'''
from PyQt5.QtCore import pyqtSignal

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
            self.signals['set_magmap'].emit(self._modelRef.magnification_map)
        except:
            print("Exception in binding magmapmodel")
        
    def setROI(self,start,end):
        print(type(start))
        vstart = Vector2D(start[0],start[1])
        vend = Vector2D(end[0],end[1])
        self._modelRef.specify_light_curve(vstart,vend)

class MagMapController2(object):
    """docstring for MagMapController"""



    def __init__(self, view):
        pass
    
    def bindFields(self):
        from ..Models import Model
        self.view.setMagMap(Model[self.modelID].magMapArray)

    def setModel(self,model):
#         if isinstance(model,la.Trial):
        from ..Models.MagnificationMapModel import MagnificationMapModel
        from ..Models import Model
        self.view._modelID = model.filename
        Model[self.modelID] = MagnificationMapModel(model)
        self.bindFields()
#         else:
#             raise ValueError("model must be of type Trial")


