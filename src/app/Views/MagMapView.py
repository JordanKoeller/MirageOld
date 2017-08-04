'''
Created on Jul 25, 2017

@author: jkoeller
'''
from pyqtgraph.graphicsItems.ImageItem import ImageItem

from .View import CanvasView
from .. import magmapUIFile
from pyqtgraph.widgets.GradientWidget import GradientWidget
from .Drawer.ShapeDrawer import drawSolidCircle

import numpy as np
from pyqtgraph.graphicsItems.ROI import LineSegmentROI

from PyQt5 import uic

class MagMapView(CanvasView):
    '''
    classdocs
    '''


    def __init__(self, modelID,title=None):
        CanvasView.__init__(self,modelID,title)
        uic.loadUi(magmapUIFile,self)
        self._viewBox = self.imgPane.addViewBox(lockAspect=True)
        self._viewBox.invertY()
        self._imgItem = ImageItem()
        self._viewBox.addItem(self._imgItem)
        self.title = "MagMap Image"
        self.type = "MagMapView"
        self.radius = 5
        self._roi = None
        
    def _setColorMap(self):
        gradient = self.gradientWidget.getLookupTable(500,alpha=False)
        self._magMapImg.setLookupTable(gradient,True)
        
    def setMagMap(self,img,baseMag):
        self._imgStatic = img
        self._imgItem.setImage(img)
        self.gradientWidget.restoreState(self._getCenteredGradient(baseMag))
        self._baseMag = int(baseMag)
        self._magMapDataCoords = np.ndarray((img.shape[0],img.shape[1],2))
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                self._magMapDataCoords[i,j] = [i,j]
                
    def _getCenteredGradient(self,center):
        default = {'ticks':[(0.0, (0, 255, 255, 255)), (1.0, (255, 255, 0, 255)), (center/self._imgStatic.max(), (0, 0, 0, 255)), (center/self._imgStatic.max()/2, (0, 0, 255, 255)), (self._imgStatic.max()/255/2, (255, 0, 0, 255))],'mode':'rgb'}
        return default
                
    def setROI(self,begin,end):
        self._roi = LineSegmentROI(begin,end,pen={'color':'#00FF00'})
        self._roi.setZValue(10)
        self._magMapPane.addItem(self._roi)
        
    def getROI(self):
        if self._roi:
            region = self._roi.getArrayRegion(self._magMapDataCoords,self._imgItem)
            return np.array(region)
        else:
            return None
        
    def setTracer(self,coords):
        img = self._imgStatic.copy()
        drawSolidCircle(int(coords[0]),int(coords[1]),10,img,255)
        self._imgItem.setImage(img,autoRange=False)
        
    def update(self,*args,**kwargs):
        self.setTracer(*args)
    
    
        
    