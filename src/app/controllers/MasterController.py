'''
Created on Dec 22, 2017

@author: jkoeller
'''
import sys

from PyQt5.QtCore import pyqtSignal

from . import Controller
from . import LightCurveController, LensedImageController, MagMapController, ParametersController, TableController
from . import AnimationRunner
from PyQt5.QtWidgets import QMessageBox

class MasterController(Controller):
    '''
    classdocs
    '''
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()
    _addView = pyqtSignal(object)
    _updateModel = pyqtSignal(object)
    _startCalculation = pyqtSignal(object,object)
    _warningLabel = pyqtSignal(str)

    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        self.lightCurveController = LightCurveController()
        self.lensedImageController = LensedImageController()
        self.tableController = TableController()
        self.parametersController = ParametersController()
        self.magMapController = MagMapController()
        self.tableController.bind_parameters_controller(self.parametersController)
        self.runner = AnimationRunner()
        self.addSignals(add_view_signal = self._addView,
                        update_model_signal = self._updateModel,
                        trigger_calculation = self._startCalculation,
                        warning = self._warningLabel)
        self.addSignals(view_update_signal = self._update_signal,
                        destroy_view = self._destroy_signal)
        
    
    def bind_to_model(self,model):
        self.model = model
        self.parametersController.bind_to_model(self.model)
    
    def bind_view_signals(self,viewSignals):
        from ..views import WindowView
        assert isinstance(viewSignals,WindowView)
        signals = viewSignals.signals
        signals['exit_signal'].connect(self.exit)
        signals['play_signal'].connect(self.playPauseSlot)
        signals['reset_signal'].connect(self.resetSlot)
        signals['save_table'].connect(self.tableController.save)
        signals['load_table'].connect(self.tableController.load)
        signals['save_setup'].connect(self.parametersController.save)
        signals['load_setup'].connect(self.parametersController.load)
        signals['record_signal'].connect(self.recordSlot)
        signals['plot_pane_signal'].connect(self.togglePlotPane)
        signals['mm_pane_signal'].connect(self.toggleMagMapPane)
        signals['param_pane_signal'].connect(self.toggleParamPane)
        signals['image_pane_signal'].connect(self.toggleImagePane)
        signals['toggle_table_signal'].connect(self.toggleTablePane)
        signals['to_analysis_perspective'].connect(self.enableAnalysis)
        signals['to_explore_perspective'].connect(self.disableAnalysis)
        signals['to_table_perspective'].connect(self.disableAnalysis)
        self.signals['add_view_signal'].connect(viewSignals.addView)
        self.signals['trigger_calculation'].connect(self.runner.trigger)
        self.signals['warning'].connect(self.raise_warning)
        
    def playPauseSlot(self):
        if self.updateModel():
            self.signals['trigger_calculation'].emit(self.model,self)
        
    def updateModel(self):
        parameters = self.parametersController.getParameters()
        if parameters:
            self.model.set_parameters(parameters)
            return True
        else:
            self.signals['warning'].emit("Error: Could not construct system parameters. Please make sure all values are input correctly.")
            return False
        
    def enableAnalysis(self):
        pass
    
    def disableAnalysis(self):
        pass
        
    def exit(self):
        self.runner.halt()
        sys.exit()
        
    def resetSlot(self):
        pass    
    def recordSlot(self):
        pass
    
    def togglePlotPane(self,state):
        from ..views import PlotView
        if state is True:
            view = PlotView()
            self.lightCurveController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.lightCurveController.signals['destroy_view'].emit()
    
    def toggleMagMapPane(self,state):
        print("Calling toggleMagMapPane " + str(state))
    
    def toggleParamPane(self,state):
        from ..views import ParametersView
        if state is True:
            view = ParametersView()
            self.parametersController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
            self.parametersController.update(self.model.parameters)
        else:
            self.parametersController.signals['destroy_view'].emit()
    
    def toggleImagePane(self,state):
        from ..views import ImageView
        if state is True:
            view = ImageView()
            self.lensedImageController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.lensedImageController.signals['destroy_view'].emit()
            print("Toggling imagePane off")
            
    def toggleTablePane(self,state):
        from ..views import TableView
        if state is True:
            view = TableView()
            self.tableController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.tableController.signals['destroy_view'].emit()
            
    def raise_warning(self,warningString):
        QMessageBox.warning(None, "Warning", warningString)