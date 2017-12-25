'''
Created on Dec 20, 2017

@author: jkoeller
'''

from PyQt5 import QtCore
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget

import numpy as np

from . import View


class ImageView(View):
    '''
    classdocs
    '''
    
    _sigPressed = QtCore.pyqtSignal(object)
    _sigDragged = QtCore.pyqtSignal(object)
    _sigReleased = QtCore.pyqtSignal(object)



    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        View.__init__(self,*args,**kwargs)
        widget = GraphicsLayoutWidget()
        viewBox = widget.addViewBox(lockAspect = True, invertY = True)
        self._imgItem = ImageItem()
        viewBox.addItem(self._imgItem)
        self.addWidget(widget)
        self.setTitle("Lensed Image")
        self.addSignals(imgRightClicked=self._sigPressed,
                        imgRightDragged=self._sigDragged,
                        imgRightReleased=self._sigReleased)
        self.dragStarted = False
        
#     def mousePressEvent(self,ev):
#         if ev.button() == QtCore.Qt.RightButton:
#             print("Right Clicked")
#             ev.accept()
#             self.dragStarted = True
#             self._sigPressed.emit(ev.pos())
#         else:
#             View.mousePressEvent(self,ev)
#             
#     def mouseMoveEvent(self,ev):
#             if self.dragStarted:
#                 self._sigDragged.emit(ev.pos())
#                 ev.accept()
#             else:
#                 View.mouseMoveEvent(self,ev)
#                 
#     def mouseReleaseEvent(self,ev):
#             if ev.button() == QtCore.Qt.RightButton:
#                 ev.accept()
#                 self.dragStarted = False
#                 self._sigReleased.emit(ev.pos())
#             else:
#                 View.mouseMoveEvent(self,ev)
                
    def setImage(self,img):
        print(type(img))
        assert isinstance(img,np.ndarray), "ImageView can only display numpy arrays of RGB values"
        self._imgItem.setImage(img)