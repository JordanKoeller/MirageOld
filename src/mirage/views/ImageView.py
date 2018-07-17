'''
Created on Dec 20, 2017

@author: jkoeller
'''

from pyqtgraph.graphicsItems.ROI import ROI
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget

import numpy as np

from . import View, CustomImageItem
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

class ImageView(View):
    '''
    classdocs
    '''
    
    _sigROISet = pyqtSignal(object,object)



    def __init__(self,*args,**kwargs):
        '''
        Constructor
        '''
        View.__init__(self,*args,**kwargs)
        widget = GraphicsLayoutWidget()
        self._viewBox = widget.addViewBox(lockAspect = True)
        self._imgItem = CustomImageItem()
        self._viewBox.addItem(self._imgItem)
        self._viewBox.invertY()
        self.addWidget(widget)
        self.setTitle("Lensed Image")
        self._imgItem.sigPressed.connect(self.pressed_slot)
        self._imgItem.sigDragged.connect(self.dragged_slot)
        self._imgItem.sigReleased.connect(self.released_slot)
        self.roiStart = None
        self.roiEnd = None
        self.dragStarted = False
        self._roi = None
        self.addSignals(ROI_set = self._sigROISet)
                
    def setImage(self,img):
        assert isinstance(img,np.ndarray), "ImageView can only display numpy arrays of RGB values"
        self._imgItem.setImage(img)
        
        
        
    def pressed_slot(self,pos):
        self.roiStart = np.array([pos.x(),pos.y()])
        
    def dragged_slot(self,pos):
        self.roiEnd = np.array([pos.x(),pos.y()])
        self.constructROI(self.roiStart, self.roiEnd)
        
    def released_slot(self,pos):
        self.roiEnd = np.array([pos.x(),pos.y()])
        self.constructROI(self.roiStart,self.roiEnd)
        response = QMessageBox.question(self,"Zoom and Enhance?",
            "Zoom in on the selected region?")
        if response:
            self.signals['ROI_set'].emit(self.roiStart,self.roiEnd)
        else:
            print("Nvm")

        
    def constructROI(self,start,end):
        if self._roi:
            self._viewBox.removeItem(self._roi)
        dims = end - start
        dimset = max(dims)
        self._roi = ROI(start,dims*0+dimset,pen = {'color':'#00FF00'},movable=False)
        self._roi.sigClicked.connect(lambda x: self.accept())
        # self._roi.addScaleHandle([0, 0], [1, 1])
        # self._roi.addScaleHandle([1, 1], [0, 0])
        self._roi.setZValue(10)
        self._viewBox.addItem(self._roi)
#         self.signals['ROI_set'].emit(self._roi)
        
    def accept(self,ev):
        ev.accept()
        print("Caught an ev")
