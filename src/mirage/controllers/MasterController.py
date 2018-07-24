'''
Created on Dec 22, 2017

@author: jkoeller
'''
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from mirage.controllers.RunnerController import LightCurveRunner

from . import AnimationRunner
from . import Controller
from . import LightCurveController, LensedImageController, MagMapController, ParametersController, TableController


class MasterController(Controller):
    '''
    classdocs
    '''
    _update_signal = pyqtSignal(object)
    _destroy_signal = pyqtSignal()
    _addView = pyqtSignal(object)
    _updateModel = pyqtSignal(object)
    _startCalculation = pyqtSignal(object, object)
    _warningLabel = pyqtSignal(str)
    _msg = pyqtSignal(str)
    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        self.lightCurveController = LightCurveController()
        self.lensedImageController = LensedImageController()
        self.lensedImageController.signals['request_zoom_on'].connect(lambda x,y: self._zoom_on(x,y))
        self.tableController = TableController()
        self.parametersController = ParametersController()
        self.magMapController = MagMapController()
        self.tableController.bind_parameters_controller(self.parametersController)
        self.runner = AnimationRunner()
        self.addSignals(add_view_signal=self._addView,
                        update_model_signal=self._updateModel,
                        warning=self._warningLabel)
        self.addSignals(view_update_signal=self._update_signal,
                        destroy_view=self._destroy_signal)
        self.addSignals(message=self._msg)

    def _zoom_on(self,tl,br):
        newP = self.model.zoom_to(tl,br)
        self.parametersController.bind_fields(newP)

        
    def clear_perspective(self):
        self.lightCurveController.signals['destroy_view'].emit()
        self.lensedImageController.signals['destroy_view'].emit()
        self.tableController.signals['destroy_view'].emit()
        self.magMapController.signals['destroy_view'].emit()
    
    def bind_to_model(self, model):
        self.model = model
        self.parametersController.bind_to_model(self.model)
        self.magMapController.bind_to_model(self.model)
    
    def bind_view_signals(self, viewSignals):
        from ..views import WindowView
        assert isinstance(viewSignals, WindowView)
        signals = viewSignals.signals
        self.parametersController.set_view(viewSignals)
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
        # signals['param_pane_signal'].connect(self.toggleParamPane)
        signals['image_pane_signal'].connect(self.toggleImagePane)
        signals['toggle_table_signal'].connect(self.toggleTablePane)
        signals['to_analysis_perspective'].connect(self.enableAnalysis)
        signals['to_explore_perspective'].connect(self.disableAnalysis)
        signals['to_table_perspective'].connect(self.disableAnalysis)
        signals['destroy_all'].connect(self.clear_perspective)
        signals['scale_mag_map'].connect(self.magMapController.setScaling)
        self.signals['add_view_signal'].connect(viewSignals.addView)
        self.signals['warning'].connect(self.raise_warning)
        self.signals['message'].connect(viewSignals.message_slot)
        
    def playPauseSlot(self):
        self.signals['message'].emit("Calculating")
        if self.updateModel():
            self.runner.trigger(self.model, self)
#             self.signals['trigger_calculation'].emit(self.model,self)

    def read_only_entry(self,state):
        self.parametersController.read_only(state)
        
    def updateModel(self):
        parameters = self.parametersController.getParameters()
        if parameters is None:
            print("Returned None, because is set to readonly")
            return True
        if parameters:
            if parameters != self.model.parameters:
                self.model.set_parameters(parameters)
                self.model.bind_parameters()
            return True
        elif parameters == False:
            self.signals['warning'].emit("Error: Could not construct system parameters. Please make sure all values are input correctly.")
            return False
        else:
            print("WHAT HAPPENED IN UPDATE MODEL???")
        
    def resetSlot(self):
        self.signals['message'].emit("Reseting")
        parameters = self.parametersController.getParameters()
        if parameters:
            self.model.set_parameters(parameters)
            self.model.bind_parameters()
        
    def enableAnalysis(self,trial=None):
        from mirage.model import TrialModel
        from mirage.lens_analysis import Trial
        if not isinstance(trial,Trial):
            from mirage.lens_analysis import load
            trial = load(None)
            if trial:
                trial = trial[0]
            else:
                return
        model = TrialModel(trial)
        self.runner = LightCurveRunner()
        self.bind_to_model(model)
        self.parametersController.bind_fields(model.parameters)
        self.parametersController.set_read_only(True)
    
    def disableAnalysis(self):
        self.runner = AnimationRunner()
        from mirage.model import ParametersModel
        self.parametersController.set_read_only(False)
        if self.model:
            self.model.disable()
            model = ParametersModel(self.model.parameters)
            self.bind_to_model(model)
        else:
            model = ParametersModel()
            self.bind_to_model(model)
        
    def exit(self):
        self.runner.halt()
        sys.exit()

    def recordSlot(self):
        pass
    
    def togglePlotPane(self, state):
        from ..views import PlotView
        if state is True:
            view = PlotView()
            self.lightCurveController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.lightCurveController.signals['destroy_view'].emit()
    
    def toggleMagMapPane(self, state):
        from ..views import MagMapView
        if state is True: 
            view = MagMapView()
            self.magMapController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.magMapController.signals['destroy_view'].emit()
    
    
    def toggleParamPane(self, state,read_only):
        self.parametersController.toggle(state,read_only)
    
    def toggleImagePane(self, state):
        from ..views import ImageView
        if state is True:
            view = ImageView()
            self.lensedImageController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.lensedImageController.signals['destroy_view'].emit()
            
    def toggleTablePane(self, state):
        from ..views import TableView
        if state is True:
            view = TableView()
            self.tableController.bind_view_signals(view)
            self.signals['add_view_signal'].emit(view)
        else:
            self.tableController.signals['destroy_view'].emit()
            
    def raise_warning(self, warningString):
        QMessageBox.warning(None, "Warning", warningString)
