from pyqtgraph.graphicsItems.GraphicsLayout import GraphicsLayout
import pyqtgraph
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from PyQt5 import QtCore
from ...Models.Model import Model
import numpy as np

from pyqtgraph import LineSegmentROI
class MagMapTracerView(object):

    def __init__(self,parent=None,signals=None,colormap=None):
        #Signals are in order of imgSignal, magMapSignal, lightCurveSignal
#         pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        self._masterPane = GraphicsLayout(parent)
        self._signals = signals
        self._masterPane.nextRow()
        self._lcPane = self._masterPane.addPlot(colspan=2) #Plot for lightcurve
        self._masterPane.nextRow()
        self._imgPaneView = self._masterPane.addViewBox(lockAspect=True) #ViewBox for img of quasar, stars, etc
        self._magMapPane = self._masterPane.addViewBox(lockAspect=True) #ViewBox for magnification map
        self._magMapImg = ImageItem() #ImageView for the magnification map
        self._magMapPane.addItem(self._magMapImg)
        self._roi = None
        self._imgPane = ImageItem() #ImageView for the starry picture
        self._imgPaneView.addItem(self._imgPane)
        self._imgPane.setLookupTable(Model.colorMap)
        signals[0].connect(self._updateImgPane)
        signals[1].connect(self._setMagMap)
        signals[2].connect(self._updateLightCurve)
        
    def _updateImgPane(self,img):
        """img should be an instance of an np.ndarray[dtype=np.uint8, ndim=2].
        AKA what Engine.build_frame() returns."""
        self._imgPane.setImage(img,autoRange=False)
        
    def _updateLightCurve(self,xVals = [], yVals = []):
        self._lcPane.plot(xVals,yVals,clear=True) 
        
        
    def _setMagMap(self,img):
        #img is a QImage instance
#         self._imgPane.setimage(pyqtgraph.imageToArray(img,copy=True))
        self._magMapImg.setImage(img,autoRange=False)
        self._magMapDataCoords = np.ndarray((img.shape[0],img.shape[1],2),dtype=np.int)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                self._magMapDataCoords[i,j] = [i,img.shape[1]-j]

    def _setROI(self,begin,end):
        if self._roi:
            self._magMapPane.removeItem(self._roi)
        self._roi = LineSegmentROI(begin,end) #ROI for magnificationMap
        self._roi.setZValue(10) #Ensure ROI is drawn above the magmap
        self._magMapPane.addItem(self._roi)
        
    def getROI(self):
        region = self._roi.getArrayRegion(self._magMapDataCoords, self._magMapImg)
        return np.array(region,dtype=np.int)
    
    
        
def autoLaunch():
    win = pyqtgraph.GraphicsLayoutWidget()
    view = MagMapTracerView()
    win.addItem(view._masterPane)
    img1 = np.random.normal(size=(100,200))
    view._setMagMap(img1)
    view._setROI([0,0],[3,3])
    return (win,view)