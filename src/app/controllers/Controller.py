'''
Created on Dec 22, 2017

@author: jkoeller
'''
from abc import abstractmethod

from PyQt5.QtCore import QObject

from app.utility import SignalRepo


class Controller(QObject, SignalRepo):
    

    _model = None
    
    def __init__(self):
        SignalRepo.__init__(self)
        QObject.__init__(self)

        
        
        
    @abstractmethod
    def bind_view_signals(self,viewSignals):
        pass
    
        
    
    def bind_to_model(self,model):
        self._model = model

    def update(self,params=None):
        self.signals['view_update_signal'].emit(params)
        