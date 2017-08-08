from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from PyQt5 import QtCore

class View(GraphicsLayoutWidget):
    """General view class that can be added to the program's layout.
    Accepts a modelID as an argument."""
    title = ''
    _signalRef = QtCore.pyqtSignal(object)

    def __init__(self, modelID='default',title=None):
        super(View, self).__init__()
        self.modelID = modelID
        self.type = ''
        if title:
            self.title = title
        self.__enabled = True

    @property
    def signal(self):
        return self._signalRef

    @property
    def enabled(self):
        return self.__enabled

    def disableUpdates(self):
        self.__enabled = False

    def enableUpdates(self):
        self.__enabled = True

class ControllerView(View):
    """abstract view with methods to get user data out of the view."""
    def __init__(self, modelID, title = None):
        View.__init__(self,modelID,title)
        modelID = 'default'

    def getValue(self):
        pass


class CanvasView(View):
    
    
    def __init__(self,modelID,title=None,*args,**kwargs):
        View.__init__(self,modelID,title)
        modelID = 'default'
        self.signal.connect(self.receiveSignal)

    def update(self,*args,**kwargs):
        pass
    
    def getFrame(self):
        pass

    def receiveSignal(self,*args):
        if self.enabled:
            self.update(*args)
 