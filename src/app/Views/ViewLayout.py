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
        self._views = []
        layout.addWidget(self._layout)
        self.setLayout(layout)
        self.mergeSignal.connect(self.mergeViews)
        
    def addView(self,view):
        dock = Dock(view.title,closable=True,mergeSignal = self.mergeSignal)
        dock.addWidget(view)
        view.sigTitleChanged.connect(dock.setTitle)
        self._layout.addDock(dock,position='right')
        dock.sigClosed.connect(lambda: self.removeView(view))
        self._views.append(view)

    def clear(self):
        # self._layout.clear()
        while self._views != []:
            self._views.remove(self._views[0])

    def removeView(self,view):
        self._views.remove(view)
        view.destroy()
        


    @property
    def views(self):
        return self._views

    def mergeViews(self,view1,view2):
        if type(view1) == type(view2) and isinstance(view1,LightCurvePlotView):
            view1.bridgeTo(view2)
        elif type(view1) == type(view2) and isinstance(view1,MagMapView):
            view2.bridgeTo(view1)
    
        
        
    def updateFrame(self,frame):
        pass
    
    def getFrame(self):
        pass
    
    @property
    def signal(self):
        return self._signal
