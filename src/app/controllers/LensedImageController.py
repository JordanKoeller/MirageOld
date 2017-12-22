'''
Created on Dec 20, 2017

@author: jkoeller
'''
import numpy as np

from . import Controller
from ..views.drawer.LensedImageDrawer import LensedImageDrawer

class LensedImageController(Controller):
    '''
    classdocs
    '''


    def __init__(self, *args,**kwargs):
        '''
        Constructor
        '''
        Controller.__init__(self,*args,**kwargs)
        from app.views import ImageView
        self._viewType = ImageView
        self._drawer = LensedImageDrawer()
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType)
        self.signals['view_update_signal'].connect(view.setImage)
        view.signals['imgRightClicked'].connect(self._createROI)
        view.signals['imgRightDragged'].connect(self._defineROI)
        view.signals['imgRightReleased'].connect(self._closeROI)
    
    def setModel(self,model):
        self._model = model
        
    def setLensedImg(self, pixValues):
        assert self._model is not None, "Must set a model before can draw lensed images"
        img = self._drawer.draw((self._model,pixValues))
        self.setImage(img)
    
    def setImage(self,img):
        assert isinstance(img, np.ndarray), "img must be a 2D numpy array."
        self.signals['view_update_signal'].emit(img)
    
    def _createROI(self,event):
        pass
    
    def _defineROI(self,event):
        pass
    
    def _closeROI(self,event):
        pass