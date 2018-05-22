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
    _setUnits = pyqtSignal(str)
    _modelRegenStars = pyqtSignal()
    _setReadOnly = pyqtSignal(bool)
    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        from app.views import ParametersView
        self._viewType = ParametersView
        self.addSignals(request_parameters=self._requestP)
        self.addSignals(view_update_signal=self._update_signal,
                        destroy_view=self._destroy_signal,
                        set_input_units=self._setUnits,
                        regenerate_stars=self._modelRegenStars,
                        set_read_only = self._setReadOnly)
        
    def bind_view_signals(self, view):
        assert isinstance(view, self._viewType), "view must be a ParametersView instance for ParametersController to bind to it."
        self.signals['view_update_signal'].connect(view.update_slot)
        self.signals['destroy_view'].connect(view.destroy)
        self.signals['request_parameters'].connect(view.getParameters)
        self.signals['set_read_only'].connect(view.set_read_only)
        view.signals['send_parameters'].connect(self.receive_parameters)
        view.signals['regenerate_stars'].connect(self.regenStars)
        view.signals['set_input_units'].connect(self.updateUnits)
        view.signals['set_input_units'].connect(lambda s: self.signals['set_input_units'].emit(s))
#         self.addSignals(set_input_units = view.signals['set_input_units'])

    def bind_to_model(self, model):
        self.signals['regenerate_stars'].connect(model.regenerate_stars)
        
    def receive_parameters(self, parameters):
        self._parameters = parameters 
    
    def getParameters(self):
        p1 = self._getPHelper()
        self.update(p1)
        p2 = self._getPHelper()
        return p2
    
    def _getPHelper(self):
        self._parameters = None
        self.signals['request_parameters'].emit()
        QApplication.processEvents() #If parameters is still None, there is no view. If parameters is False, threw an error. If returns Parameters object, was successful
        parameters = self._parameters
        self._parameters = None
        return parameters
    
    def regenStars(self):
        self.signals['regenerate_stars'].emit()
    
    def updateUnits(self):
        pass
    
    def save(self):
        from app.io import ParametersFileManager
        data = self.getParameters()
        if data:
            filemanager = ParametersFileManager()
            filemanager.open()
            filemanager.write(data)
            filemanager.close()
    
    def load(self):
        from app.io import ParametersFileReader
        filemanager = ParametersFileReader()
        if filemanager.open():
            params = filemanager.load()
            filemanager.close()
            self.update(params)
            
    def read_only(self,state):
        self.signals['set_read_only'].emit(state)
        print("Set as read-only parameters controller")
