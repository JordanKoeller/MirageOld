'''
Created on Dec 20, 2017

@author: jkoeller
'''
from PyQt5.QtCore import pyqtSignal

import numpy as np

from . import Controller
from ..drawer.LensedImageDrawer import LensedImageDrawer
from mirage.utility import Vector2D

class LensedImageController(Controller):
    '''
    classdocs
    '''
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()
    _ROI_set = pyqtSignal(object,object)

    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        from mirage.views import ImageView
        self._viewType = ImageView
        self._drawer = LensedImageDrawer()
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal,
                        request_zoom_on = self._ROI_set)
        self.img_shape = None 
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType)
        self.signals['view_update_signal'].connect(view.setImage)
        self.signals['destroy_view'].connect(view.destroy)
        view.signals['ROI_set'].connect(lambda x,y: self.zoom_on_roi(x,y))
    
    def setModel(self,model):
        self._model = model
        
    def setLensedImg(self,model,pixValues):
        assert model is not None, "Must set a model before can draw lensed images"
        img = self._drawer.draw((model,pixValues))
        self.setImage(img)
        self.img_shape = img.shape
    
    def setImage(self,img):
        assert isinstance(img, np.ndarray), "img must be a 2D numpy array."
        self.signals['view_update_signal'].emit(img)
        
    def zoom_on_roi(self,s,e):
        tl,br = s,e
        s = [s[0],self.img_shape[1] - s[1]]
        e = [e[0],self.img_shape[1] - e[1]]
        dims = Vector2D(e[0]-s[0],e[1]-s[1])
        center = Vector2D((e[0]+s[0])/2,(e[1] + s[1])/2)
        self.signals['request_zoom_on'].emit(center,dims)
        
    
    
