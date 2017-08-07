from PyQt5.QtWidgets import QFrame, QVBoxLayout
from PyQt5 import QtCore
from .dockarea.Dock import Dock
from .dockarea.DockArea import DockArea
from .View import CanvasView, ControllerView
from .CompositeView import CompositeView
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
        self.mergeSignal.connect(self.mergePlots)
        
    def addView(self,view):
        dock = Dock(view.title,closable=True,mergeSignal = self.mergeSignal)
        dock.addWidget(view)
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
    @property
    def canvasViews(self):
        return self._canvasViews

    def mergePlots(self,plot1,plot2):
        print("Merging")
        plot1.disableUpdates()
        plot2.disableUpdates()
        self.composite = CompositeView(plot1,plot2)
    
        
        
    def updateFrame(self,frame):
        pass
    
    def getFrame(self):
        pass
    
    @property
    def signal(self):
        return self._signal
