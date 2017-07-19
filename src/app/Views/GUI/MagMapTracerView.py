from PyQt5 import QtCore
from pyqtgraph import LineSegmentROI
from pyqtgraph.graphicsItems.ImageItem import ImageItem

import numpy as np

from ...Utility.NullSignal import NullSignal
from ...Views.Drawer.ShapeDrawer import drawSolidCircle


class MagMapTracerView(QtCore.QObject):
    
    hasUpdated = QtCore.pyqtSignal(object)

    def __init__(self,masterFrame,plotFrame,imgFrame,gradientFrame,masterSignal = NullSignal):
        #Signals are in order of imgSignal, magMapSignal, lightCurveSignal
        QtCore.QObject.__init__(self)
        # pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        self._gradientFrame = gradientFrame
        self._gradientFrame.addTick(0.5)
        self._gradientFrame.sigGradientChanged.connect(self._setColorMap)
        self._lcPane = plotFrame
        self._imgPane = imgFrame
        self._masterPane = masterFrame
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
        if masterSignal:
            masterSignal.connect(self.updateAll)
    
    def updateAll(self,img,lc,tracerPos):
        self._updateImgPane(img)
        self._updateLightCurve(lc[0],lc[1])
        self._positionTracer(tracerPos)
#         self.hasUpdated.emit(self.getFrame())

    def _setColorMap(self):
#         print(self._gradientFrame.getLookupTable(500,alpha=False))
        self._magMapImg.setLookupTable(self._gradientFrame.getLookupTable(500,alpha=False), True)

    def setUpdatesEnabled(self,tf):
        self._masterPane.setHidden(tf)
        

    def _updateImgPane(self,img):
        """img should be an instance of an np.ndarray[dtype=np.uint8, ndim=2].
        AKA what Engine.build_frame() returns."""
        self._img = img
        self._imgView.setImage(self._img,autoRange=False)
        
    def _updateLightCurve(self,xVals = [], yVals = []):
        if xVals != [] and yVals != []:
            self._lcPane.plot(xVals,yVals,clear=True,pen={'width':5})
            
    def _getCenteredGradient(self,center):
        print(center/self._imgStatic.max())
        default = {'ticks':[(0.0, (0, 255, 255, 255)), (1.0, (255, 255, 0, 255)), (center/self._imgStatic.max(), (0, 0, 0, 255)), (center/self._imgStatic.max()/2, (0, 0, 255, 255)), (self._imgStatic.max()/255/2, (255, 0, 0, 255))],'mode':'rgb'}
        return default
        
    def setMagMap(self,img,baseMag):
        #img is a QImage instance
        self._imgStatic = img
        self._magMapImg.setImage(img)
        self._gradientFrame.restoreState(self._getCenteredGradient(baseMag))
        self._baseMag = int(baseMag)
        self._magMapDataCoords = np.ndarray((img.shape[0],img.shape[1],2))
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                self._magMapDataCoords[i,j] = [i,j]
        self._setROI([50,50])

    def _setROI(self,begin):
        if self._roi:
            self._magMapPane.removeItem(self._roi)
        self._roi = LineSegmentROI(begin,pen={'color':'#00FF00','width':3}) #ROI for magnificationMap
        self._roi.setZValue(10) #Ensure ROI is drawn above the magmap
        self._magMapPane.addItem(self._roi)
        
        
    def _positionTracer(self,coords):
        img = self._imgStatic.copy()
        drawSolidCircle(int(coords[0]),int(coords[1]),10,img,255)
        self._magMapImg.setImage(img,autoRange=False)

        
        
    def getROI(self):
        region = self._roi.getArrayRegion(self._magMapDataCoords, self._magMapImg)
        self._lcPane.setXRange(0,len(region))
        return np.array(region)
    
    def getFrame(self):
        self._masterPane.repaint()
        return self._masterPane.grab()
    
    
    