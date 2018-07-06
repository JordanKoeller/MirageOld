'''
Created on Dec 20, 2017

@author: jkoeller
'''
from PyQt5.QtCore import pyqtSignal

import numpy as np

from . import Controller
from ..drawer.LensedImageDrawer import LensedImageDrawer


class LensedImageController(Controller):
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
        from mirage.views import ImageView
        self._viewType = ImageView
        self._drawer = LensedImageDrawer()
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal)
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType)
        self.signals['view_update_signal'].connect(view.setImage)
        self.signals['destroy_view'].connect(view.destroy)
#         view.signals['imgRightClicked'].connect(self._createROI)
#         view.signals['imgRightDragged'].connect(self._defineROI)
#         view.signals['imgRightReleased'].connect(self._closeROI)
        view.signals['ROI_set'].connect(self.zoom_on_roi)
    
    def setModel(self,model):
        self._model = model
        
    def setLensedImg(self,model,pixValues):
        assert model is not None, "Must set a model before can draw lensed images"
        img = self._drawer.draw((model,pixValues))
        self.setImage(img)
    
    def setImage(self,img):
        assert isinstance(img, np.ndarray), "img must be a 2D numpy array."
        self.signals['view_update_signal'].emit(img)
        
    def zoom_on_roi(self,roi):
        print("Should zoom")
        pass
    
    
