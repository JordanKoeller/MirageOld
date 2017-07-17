import pyqtgraph
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from PyQt5 import QtCore
from ...Models.Model import Model
import numpy as np
from ...Utility.NullSignal import NullSignal
from ...Views.Drawer.ShapeDrawer_rgb import drawSolidCircle_rgb

from pyqtgraph import LineSegmentROI
from pyqtgraph.graphicsItems.ROI import CircleROI
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from PIL import ImageDraw

class MagMapTracerView(QtCore.QObject):
    
    hasUpdated = QtCore.pyqtSignal(object)

    def __init__(self,view,masterSignal = NullSignal):
        #Signals are in order of imgSignal, magMapSignal, lightCurveSignal
        QtCore.QObject.__init__(self)
        # pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        self.view = view
        self._lcPane = self.view.tracerPlot #Plot for lightcurve
        self._imgPane = self.view.tracerImgArea
        self._imgPaneView = self._imgPane.addViewBox(lockAspect=True) #ViewBox for img of quasar, stars, etc
        self._magMapPane = self._imgPane.addViewBox(lockAspect=True) #ViewBox for magnification map
        self._magMapPane.invertY()
        self._imgPaneView.invertY()
        self._magMapImg = ImageItem() #ImageView for the magnification map
        self._magMapPane.addItem(self._magMapImg)
        self._roi = None
        self._tracer = None
        self._imgView = ImageItem() #ImageView for the starry picture
        self._imgPaneView.addItem(self._imgView)
        masterSignal.connect(self.updateAll)
    
    def updateAll(self,img,lc,tracerPos):
        self._updateImgPane(img)
        self._updateLightCurve(lc[0],lc[1])
        self._positionTracer(tracerPos)
#         self.hasUpdated.emit(self.getFrame())

    def setUpdatesEnabled(self,tf):
        self.view.tracerPlot.setUpdatesEnabled(tf)
        self.view.tracerImgArea.setUpdatesEnabled(tf)
        

    def _updateImgPane(self,img):
        """img should be an instance of an np.ndarray[dtype=np.uint8, ndim=2].
        AKA what Engine.build_frame() returns."""
        self._img = img
        self._imgView.setImage(self._img,autoRange=False)
        
    def _updateLightCurve(self,xVals = [], yVals = []):
        if xVals != [] and yVals != []:
            self._lcPane.plot(xVals,yVals,clear=True)
        
        
    def setMagMap(self,img):
        #img is a QImage instance
        self._imgStatic = img
        self._magMapImg.setImage(img)
        self._magMapDataCoords = np.ndarray((img.shape[0],img.shape[1],2))
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                self._magMapDataCoords[i,j] = [i,j]
        self._setROI([50,50])

    def _setROI(self,begin):
        if self._roi:
            self._magMapPane.removeItem(self._roi)
        self._roi = LineSegmentROI(begin) #ROI for magnificationMap
        self._roi.setZValue(10) #Ensure ROI is drawn above the magmap
        self._magMapPane.addItem(self._roi)
        
        
    def _positionTracer(self,coords):
        img = self._imgStatic.copy()
        drawSolidCircle_rgb(int(coords[0]),int(coords[1]),5,img,2)
        self._magMapImg.setImage(img,autoRange=False)

        
        
    def getROI(self):
        region = self._roi.getArrayRegion(self._magMapDataCoords, self._magMapImg)
        self._lcPane.setXRange(0,len(region))
        return np.array(region)
    
    def getFrame(self):
        return self.view.magTracerFrame.grab()
    
    
    