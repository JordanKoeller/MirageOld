import pyqtgraph
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from PyQt5 import QtCore
from ...Models.Model import Model
import numpy as np
from ...Utility.NullSignal import NullSignal

from pyqtgraph import LineSegmentROI
from pyqtgraph.graphicsItems.ROI import CircleROI
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget

class MagMapTracerView(QtCore.QObject):
    
    hasUpdated = QtCore.pyqtSignal(object)

    def __init__(self,parent=None,imgSignal=NullSignal,lightCurveSignal=NullSignal,magMapSignal=NullSignal,masterSignal = NullSignal):
        #Signals are in order of imgSignal, magMapSignal, lightCurveSignal
        QtCore.QObject.__init__(self)
        pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        self._masterPane = GraphicsLayoutWidget(parent,border = True)
        self._masterPane.nextRow()
        self._lcPane = self._masterPane.addPlot(colspan=2) #Plot for lightcurve
        self._masterPane.nextRow()
        self._imgPaneView = self._masterPane.addViewBox(lockAspect=True) #ViewBox for img of quasar, stars, etc
        self._magMapPane = self._masterPane.addViewBox(lockAspect=True,enableMouse=False) #ViewBox for magnification map
        self._magMapPane.invertY()
        self._imgPaneView.invertY()
        self._magMapImg = ImageItem() #ImageView for the magnification map
        self._magMapPane.addItem(self._magMapImg)
        self._roi = None
        self._tracer = None
        self._imgPane = ImageItem() #ImageView for the starry picture
        self._imgPaneView.addItem(self._imgPane)
#         imgSignal.connect(self._updateImgPane)
#         magMapSignal.connect(self._positionTracer)
#         lightCurveSignal.connect(self._updateLightCurve)
        masterSignal.connect(self.updateAll)
        
    @property
    def view(self):
        return self._masterPane
    
    def updateAll(self,img,lc,tracerPos):
        self._updateImgPane(img)
        self._updateLightCurve(lc[0],lc[1])
        self._positionTracer(tracerPos)
        self._masterPane.update()
#         self.hasUpdated.emit(self.getFrame())
        

    def _updateImgPane(self,img):
        """img should be an instance of an np.ndarray[dtype=np.uint8, ndim=2].
        AKA what Engine.build_frame() returns."""
        self._imgPane.setImage(img,autoRange=False)
        
    def _updateLightCurve(self,xVals = [], yVals = []):
        if xVals != [] and yVals != []:
            self._lcPane.plot(xVals,yVals,clear=True)
        
        
    def setMagMap(self,img):
        #img is a QImage instance
#         self._imgPane.setimage(pyqtgraph.imageToArray(img,copy=True))
        self._magMapImg.setImage(img)
        self._magMapDataCoords = np.ndarray((img.shape[0],img.shape[1],2))
        print(self._magMapDataCoords.shape)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                self._magMapDataCoords[i,j] = [img.shape[1]-j,img.shape[0]-i]
        self._setROI([50,50])

    def _setROI(self,begin):
        if self._roi:
            self._magMapPane.removeItem(self._roi)
        self._roi = LineSegmentROI(begin) #ROI for magnificationMap
        self._roi.setZValue(10) #Ensure ROI is drawn above the magmap
        self._magMapPane.addItem(self._roi)
        
        
    def _positionTracer(self,coords):
        if self._tracer == None:
            self._tracer = CircleROI(coords,(5,5),movable=False)
            self._magMapPane.addItem(self._tracer)
        else:
            self._tracer.setPos(coords[0],coords[1])
        
        
    def getROI(self):
        region = self._roi.getArrayRegion(self._magMapDataCoords, self._magMapImg)
#         print(region)
        return np.array(region)
    
    def getFrame(self):
        return self._masterPane.grab()
    
    
    