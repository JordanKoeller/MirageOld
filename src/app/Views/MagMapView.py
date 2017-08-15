'''
Created on Jul 25, 2017

@author: jkoeller
'''
from pyqtgraph.graphicsItems.MagMapImageItem import MagMapImageItem

from .View import CanvasView
from .. import magmapUIFile
from pyqtgraph.widgets.GradientWidget import GradientWidget
from .Drawer.ShapeDrawer import drawSolidCircle_Gradient
from .CompositeView import CompositeMagMap
import numpy as np
from pyqtgraph.graphicsItems.ROI import LineSegmentROI

from PyQt5 import uic, QtCore

class MagMapView(CanvasView):
    '''
    classdocs
    '''

    sigROISet = QtCore.pyqtSignal(object,object)

    def __init__(self, modelID='default',title=None):
        CanvasView.__init__(self,modelID,title)
        uic.loadUi(magmapUIFile,self)
        self._viewBox = self.imgPane.addViewBox(lockAspect=True)
        self._viewBox.invertY()
        self._imgItem = MagMapImageItem()
        self._viewBox.addItem(self._imgItem)
        # self.title = "MagMap Image"
        self.type = "MagMapView"
        self.radius = 5
        self._roi = None
        self.roiStartPos = None
        self.roiEndPos = None
        self.startDrag = False
        self._imgItem.sigPressed.connect(self._mkROI)
        self._imgItem.sigDragged.connect(self._mvROI)
        self._imgItem.sigReleased.connect(self._finishROI)
        self.gradientWidget.sigGradientChanged.connect(self._setColorMap)


    def _setColorMap(self):
        gradient = self.gradientWidget.getLookupTable(500,alpha=False)
        self._imgItem.setLookupTable(gradient,True)
        
    def setMagMap(self,img,baseMag):
        self._imgStatic = img.copy()
        self._imgItem.setImage(self._imgStatic)
        self.gradientWidget.restoreState(self._getCenteredGradient(baseMag))
        self._baseMag = int(baseMag)
                
    def _getCenteredGradient(self,center):
        default = {'ticks':[(0.0, (0, 255, 255, 255)), (1.0, (255, 255, 0, 255)), (center/self._imgStatic.max(), (0, 0, 0, 255)), (center/self._imgStatic.max()/2, (0, 0, 255, 255)), (self._imgStatic.max()/255/2, (255, 0, 0, 255))],'mode':'rgb'}
        return default
                
    def setROI(self,begin,end):
        self._viewBox.removeItem(self._roi)
        self._roi = LineSegmentROI((begin,end),pen={'color':'#00FF00'})
        self._roi.setZValue(10)
        self._viewBox.addItem(self._roi)
        self.roiStartPos = begin
        self.roiEndPos = end
        
    def getROI(self):
        return (self.roiStartPos,self.roiEndPos)

    def _mkROI(self,pos):
        self.roiStartPos = [pos.x(),pos.y()]
        self.startDrag = True
        self.setROI(self.roiStartPos,self.roiStartPos)

    def _mvROI(self,pos):
        self.roiEndPos = [pos.x(),pos.y()]
        self.setROI(self.roiStartPos,self.roiEndPos)

    def _finishROI(self,pos):
        self.startDrag = False
        self.sigROISet.emit(self.roiStartPos,self.roiEndPos)

    def setTracer(self,model,coords):
        img = self._imgStatic.copy()
        drawSolidCircle_Gradient(int(coords[0]),int(coords[1]),10,img,float(255))
        self._imgItem.setImage(img,autoRange=False)
        
    def update(self,args):
        self.setTracer(*args)
    

    def setBridge(self,bridge):
        self._bridge = bridge

    def bridgeTo(self,view):
        if not self._bridge and not view._bridge:
            CompositeMagMap(self,view)
            # view.setBridge(self._bridge)
        elif not self._bridge:
            view._bridge.addView(self)
        else:
            self._bridge.addView(view)
        
    