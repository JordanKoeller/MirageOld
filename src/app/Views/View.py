from PyQt5 import QtCore

from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget


class View(GraphicsLayoutWidget):
    """General view class that can be added to the program's layout.
    Accepts a modelID as an argument."""
    _signalRef = QtCore.pyqtSignal(object)
    sigTitleChanged = QtCore.pyqtSignal(str)

    def __init__(self, modelID='default',title=None):
        super(View, self).__init__()
        self._modelID = modelID
        self.type = ''
        self._bridge = None
        # if title:
        #     self.title = title
        # self.__enabled = True
        
    def setModelID(self,string):
        self._modelID = string
        self.sigTitleChanged.emit(self.title)

    @property
    def signal(self):
        return self._signalRef
    
    @property
    def modelID(self):
        return self._modelID

    @property
    def enabled(self):
        # print(self._bridge)
        return self._bridge == None

    @property
    def title(self):
        return self.modelID + " " + self.type

    # def disableUpdates(self):
    #     self.__enabled = False

    # def enableUpdates(self):
    #     self.__enabled = True

    def bridgeTo(self,view):
        self._bridge = bridge

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

class ViewBridge(object):
    def __init__(self,*views):
        self._views = []
        self._dataBin = []
        for view in views[::-1]:
            self.addView(view)

    def addView(self,view):
        # if isinstance(view,self._DTYPE):
        view.signal.connect(self.update)
        view.setBridge(self)
        # view.disableUpdates()
        self._views.append(view)
        # view.bridgeTo(self)

    def update(self,data):
        pass
