from PyQt5.QtWidgets import QFrame, QVBoxLayout
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea


class ViewLayout(QFrame):
    
    def __init__(self,signal,parent=None):
        QFrame.__init__(self,parent)
        self._signal = signal
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self._layout = DockArea()
        layout.addWidget(self._layout)
        self.setLayout(layout)
        
    def addView(self,view):
        dock = Dock(view.title,closable=True)
        dock.addWidget(view)
        self._layout.addDock(dock)

    def clear(self):
        self._layout.clear()
    
        
        
    def updateFrame(self,frame):
        pass
    
    def getFrame(self):
        pass
    
    @property
    def signal(self):
        return self._signal
