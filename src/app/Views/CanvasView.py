from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from PyQt5 import QtCore

class CanvasView(GraphicsLayoutWidget):
    
    title = "CanvasView"

    _signalRef = QtCore.pyqtSignal(object)    

    def __init__(self,modelID,*args,**kwargs):
        GraphicsLayoutWidget.__init__(self)
        self._modelID = modelID
    
    def update(self,*args,**kwargs):
        pass
    
    def getFrame(self):
        pass
 
    @property
    def signal(self):
        return self._signalRef