'''
Created on Dec 30, 2017

@author: jkoeller
'''


from PyQt5 import QtCore, uic
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from pyqtgraph.graphicsItems.ROI import LineSegmentROI
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget

from app import magmapUIFile
from app.drawer.ShapeDrawer import drawSolidCircle_Gradient


from . import View


class MagMapImageItem(ImageItem):
        """Extends ImageItem with its own mousePressEvent, mouseDragEvent, and mouseReleaseEvent methods to handle click-and-drag production
        of linear ROI objects.

        Any initialization parameters passed in are passed on to ImageItem.

        Intercepts RightClick MouseEvents and sends them on with the three signals

        sigPressed(QtCore.QPoint) of where the mouse event occurred.
        sigDragged(QtCore.QPoint) of where the mouse event occurred.
        sigReleased(QtCore.QPoint) of where the mouse event occurred."""

        sigPressed = QtCore.pyqtSignal(object)
        sigDragged = QtCore.pyqtSignal(object)
        sigReleased = QtCore.pyqtSignal(object)

        def __init__(self, *args, **kwargs):
                ImageItem.__init__(self,*args,**kwargs)
                self.dragStarted = False


        def mousePressEvent(self,ev):
                if ev.button() == QtCore.Qt.RightButton:
                        ev.accept()
                        self.dragStarted = True
                        self.sigPressed.emit(ev.pos())
                else:
                        ImageItem.mousePressEvent(self,ev)

        def mouseMoveEvent(self,ev):
                if self.dragStarted:
                        self.sigDragged.emit(ev.pos())
                        ev.accept()
                else:
                        ImageItem.mouseMoveEvent(self,ev)
        def mouseReleaseEvent(self,ev):
                if ev.button() == QtCore.Qt.RightButton:
                        ev.accept()
                        self.dragStarted = False
                        self.sigReleased.emit(ev.pos())
                else:
                        ImageItem.mouseMoveEvent(self,ev)









class MagMapViewWidget(GraphicsLayoutWidget):
    '''
    classdocs
    '''

    sigROISet = QtCore.pyqtSignal(object,object)

    def __init__(self):
        View.__init__(self)
        uic.loadUi(magmapUIFile,self)
        self._viewBox = self.imgPane.addViewBox(lockAspect=True)
        self._viewBox.invertY()
        self._imgItem = MagMapImageItem()
        self._viewBox.addItem(self._imgItem)
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
        
    def setMagMap(self,img,baseMag=0):
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

    def setTracer(self,coords):
        img = self._imgStatic.copy()
        drawSolidCircle_Gradient(int(coords[0]),int(coords[1]),10,img,float(255))
        self._imgItem.setImage(img,autoRange=False)
        
    def update(self,args):
        self.setTracer(*args)
        
        
class MagMapView(View):
    
    def __init__(self):
        View.__init__(self)
        self.widget = MagMapViewWidget()
        self.addWidget(self.widget)
        self.addSignals(ROI_set = self.widget.sigROISet)
        
    def update_slot(self,model,quasar_pos):
        self.widget.update(model,quasar_pos)
        
    def setTracer(self,model,coords):
        self.widget.setTracer(model, coords)
    
    def getROI(self):
        return self.widget.getROI()
    
    def setROI(self,begin,end):
        self.widget.setROI(begin, end)
        
    def setMagMap(self,img,base_mag = 1.0):
        self.widget.setMagMap(img, base_mag)