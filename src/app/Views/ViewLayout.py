from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame, QVBoxLayout

from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea

from .CompositeView import CompositePlot, CompositeMagMap
from .LightCurvePlotView import LightCurvePlotView
from .MagMapView import MagMapView
from .View import CanvasView, ControllerView


class ViewLayout(QFrame):


    sigModelDestroyed = QtCore.pyqtSignal(object)
    mergeSignal = QtCore.pyqtSignal(object,object)

    def __init__(self,signal,parent=None):
        QFrame.__init__(self,parent)
        self._signal = signal
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self._layout = DockArea()
        self._canvasViews = []
        self._modelViews = []
        layout.addWidget(self._layout)
        self.setLayout(layout)
        self.mergeSignal.connect(self.mergeViews)
        
    def addView(self,view):
        dock = Dock(view.title,closable=True,mergeSignal = self.mergeSignal)
        dock.addWidget(view)
        view.sigTitleChanged.connect(dock.setTitle)
        self._layout.addDock(dock,position='right')
        dock.sigClosed.connect(self.removeView)
        if isinstance(view,CanvasView):
            self._canvasViews.append(view)
        elif isinstance(view,ControllerView):
            self._modelViews.append(view)

    def clear(self):
        self._layout.clear()

    def removeView(self,view):
        for widget in view.widgets:
            if widget in self._canvasViews:
                self._canvasViews.remove(widget)
            elif isinstance(widget,ControllerView):
                self.sigModelDestroyed.emit(widget)

    def _removeCanvasView(self,view):
        if view in self._canvasViews:
            self._canvasViews.remove(view)

    @property
    def canvasViews(self):
        return self._canvasViews

    def mergeViews(self,view1,view2):
        # if isinstance(view1,CompositeView):
        #     view1.addView(view2)
        # if isinstance(view2,CompositeView):
        #     view2.addView(view1)
        if type(view1) == type(view2) and isinstance(view1,LightCurvePlotView):
            view1.bridgeTo(view2)
            # self._removeCanvasView(view1)
            # self._canvasViews.append(composite)
        elif type(view1) == type(view2) and isinstance(view1,MagMapView):
            view2.bridgeTo(view1)
            # self._removeCanvasView(view1)
            # composite = CompositeMagMap(view1,view2)
            # self._canvasViews.append(composite)
    
        
        
    def updateFrame(self,frame):
        pass
    
    def getFrame(self):
        pass
    
    @property
    def signal(self):
        return self._signal