'''
Created on Dec 22, 2017

@author: jkoeller
'''
from abc import abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal

from app.utility import SignalRepo


class Controller(QObject, SignalRepo):
    
    __update_signal = pyqtSignal(object)
    _viewType = None
    _model = None
    
    def __init__(self,*args,**kwargs):
        SignalRepo.__init__(self,*args,**kwargs)
        QObject.__init__(self,*args,**kwargs)
        self.addSignals(view_update_signal = self.__update_signal)
        
        
        
    @abstractmethod
    def bind_view_signals(self,viewSignals):
        pass
    
    def spawn_view(self):
        view = self._viewType()
        self.bind_view_signals(view)
        return view
        
    
    def bind_to_model(self,model):
        self._model = model
