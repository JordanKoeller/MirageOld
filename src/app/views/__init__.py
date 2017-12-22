from abc import ABC, abstractclassmethod, abstractproperty, abstractmethod, \
    ABCMeta

from pyqtgraph.dockarea.Dock import Dock

from app.utility import SignalRepo


class View(Dock, SignalRepo):
    
    def __init__(self,*args,**kwargs):
        SignalRepo.__init__(self,*args,**kwargs)
        Dock.__init__(self,None)
        self.addSignals(view_closed = self.sigClosed)
        
        
    @abstractmethod
    def update_slot(self,args):
        pass
    

from .PlotView import PlotView
from .ImageView import ImageView