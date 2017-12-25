'''
Created on Dec 22, 2017

@author: jkoeller
'''
from . import Controller
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

class ParametersController(Controller):
    '''
    classdocs
    '''
    
    _requestP = pyqtSignal()
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()

    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        from app.views import ParametersView
        self._viewType = ParametersView
        self.addSignals(request_parameters = self._requestP)
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal)
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType), "view must be a ParametersView instance for ParametersController to bind to it."
        self.signals['view_update_signal'].connect(view.update_slot)
        self.signals['destroy_view'].connect(view.destroy)
        self.signals['request_parameters'].connect(view.getParameters)
        view.signals['send_parameters'].connect(self.receive_parameters)
        view.signals['regenerate_stars'].connect(self.regenStars)
        view.signals['set_input_units'].connect(self.updateUnits)
        
    def receive_parameters(self,parameters):
        self._parameters = parameters
    
    def getParameters(self):
        self._parameters = None
        self.signals['request_parameters'].emit()
        QApplication.processEvents()
        parameters =  self._parameters
        self._parameters = None
        return parameters
    
    def regenStars(self):
        pass
    
    def updateUnits(self):
        pass
    
    def save(self):
        pass
    
    def load(self):
        pass