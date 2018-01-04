'''
Created on Dec 22, 2017

@author: jkoeller
'''
from app.calculator.ExperimentResultCalculator import varyTrial
from app.parameters.ExperimentParams import LightCurveParameters, \
    MagMapParameters, StarFieldData, ExperimentParams
from app.utility.ParametersError import ParametersError

from . import Controller
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication



class TableController(Controller):
    '''
    classdocs
    '''
    
    _add_expt_signal = pyqtSignal(object,int)
    _setUnits = pyqtSignal(str)
    _setUpdateText = pyqtSignal(str)
    _setEditEnabled = pyqtSignal(bool)
    _updateSignal = pyqtSignal(object)
    _clearTable = pyqtSignal()
    _requestTable = pyqtSignal()
    
    def __init__(self):
        '''
        Constructor
        '''
        Controller.__init__(self)
        self.editing = -1
        self.pc = None
        self.addSignals(add_experiment = self._add_expt_signal,
                        set_update_text = self._setUpdateText,
                        set_enabled_edit = self._setEditEnabled,
                        clear_table = self._clearTable,
                        set_input_units = self._setUnits,
                        request_table = self._requestTable)
        self.addSignals(view_update_signal = self._updateSignal)
        self._table = None

    def bind_view_signals(self,view):
        s = view.signals
        s['send_extras'].connect(self.addToQueue)
        s['cancel_queue_edit'].connect(self.cancelEdit)
        s['save_table'].connect(self.save)
        s['editing_params'].connect(self.editParams)
        self.signals['add_experiment'].connect(view.addExperiment)
        self.signals['set_input_units'].connect(view.set_input_units)
        s['send_table'].connect(self.receiveTable)
        self.signals['set_update_text'].connect(view.widget.addToQueueButton.setText)
        self.signals['set_enabled_edit'].connect(view.widget.queueEditCancelButton.setEnabled)
        self.signals['view_update_signal'].connect(view.update_slot)
        self.signals['clear_table'].connect(view.clear)
        self.signals['request_table'].connect(view.sendTable)
        
    def bind_parameters_controller(self,pc):
        s = pc.signals
        s['set_input_units'].connect(self.set_input_units)
        self.pc = pc
        
    def receiveTable(self,table):
        self._table = table
        
        
    def set_input_units(self,units):
        self.signals['set_input_units'].emit(units)
        
    def editParams(self,params,row):
        self.pc.update(params)
        self.update(params)
        self.editing = row
        self.signals['set_update_text'].emit("Update")
        self.signals['set_enabled_edit'].emit(True)
                
    def addToQueue(self,extras):
        parameters = self.pc.getParameters()
        if extras != "PARSE_ERROR" and parameters:
            exp = self.buildObject(extras,parameters)
            if exp:
                self.signals['add_experiment'].emit(exp,self.editing)
                if self.editing != -1:
                    self.cancelEdit()
                
    def buildObject(self,extras,parameters):
        extraObjects = []
        if 'lightcurve' in extras['datasets']:
            extraObjects.append(LightCurveParameters(extras['datasets']['lightcurve']['resolution'],
                                                              extras['datasets']['lightcurve']['pstart'],
                                                              extras['datasets']['lightcurve']['pend']))
        if 'magmap' in extras['datasets']:
            extraObjects.append(MagMapParameters(extras['datasets']['magmap']['magmapdims'],
                                                      extras['datasets']['magmap']['magmapres']))
        if extras['datasets']['starfield']:
            extraObjects.append(StarFieldData())
        exptParams = ExperimentParams(extras['name'],
                                      extras['desc'],
                                      extras['numTrials'],
                                      extras['varianceStr'],
                                      extraObjects)
        parameters.extras = exptParams
        try:
            varyTrial(parameters,0)
            return parameters
        except ParametersError as e:
            raise ParametersError(e.value)   
        except:
            raise SyntaxError("Syntax error found in trial variance code") 
                
    def save(self):
        from app.io import TableFileWriter
        data = self.getExperiments()
        if data:
            filemanager = TableFileWriter()
            filemanager.open()
            filemanager.write(data)
            filemanager.close()
            
    def getExperiments(self):
        self._table = None
        self.signals['request_table'].emit()
        QApplication.processEvents()
        if self._table:
            table = self._table
            self._table = None
            return table
        else:
            return None
        
    def load(self):
        from app.io import TableFileReader
        tableFileManager = TableFileReader()
        tableFileManager.open()
        tableFull = tableFileManager.load()
        if tableFull:
            self.signals['clear_table'].emit()
            for expt in tableFull:
                self.signals['add_experiment'].emit(expt)
            
            
    def cancelEdit(self):
        self.signals['set_enabled_edit'].emit(False)
        self.signals['set_update_text'].emit("Add to Queue")
        self.editing = -1
        


