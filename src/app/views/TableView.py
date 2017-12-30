'''
Created on Dec 25, 2017

@author: jkoeller
'''
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QPushButton
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from pyqtgraph.widgets.TableWidget import TableWidget

from app import tableUIFile
from app.views import View
from app.utility import Vector2D
from PyQt5.QtCore import pyqtSignal


class ExperimentQueueTable(TableWidget):


    editingSignal = QtCore.pyqtSignal(object,int)

    def __init__(self,parent=None,editable = True): 
        """ datain: a list of QueueEntries
            headerdata: a list of strings
        """
        TableWidget.__init__(self,parent,editable=editable)
        self.__experiments = []
        self.__initClearTable()

        
    def addExperiment(self, experiment):
        self.experiments.append(experiment)
        txtRow = self.__mkRow(experiment)
        TableWidget.addRow(self, txtRow)
        exptButton = QPushButton()
        exptButton.setText("Edit")
        exptButton.setMinimumWidth(50)
        exptButton.clicked.connect(lambda: self.editingSignal.emit(experiment,self.numRows-1))
        self.setCellWidget(self.numRows,len(txtRow),exptButton)
        clearButton = QPushButton()
        clearButton.setText("Remove")
        clearButton.setMinimumWidth(50)
        clearButton.clicked.connect(lambda: self.removeItem(experiment))
        self.setCellWidget(self.numRows,len(txtRow)+1,clearButton)

    def removeItem(self,expt):
        tmp = self.experiments[:]
        self.clear()
        self.__initClearTable()
        self.__experiments = []
        for i in tmp:
            if i is not expt:
                self.addExperiment(i)


    def clearTable(self):
        self.__initClearTable()
        
    def updateExperiment(self,exp,num):
        self.experiments[num] = exp
        tmp = self.experiments[:]
        self.clear()
        self.__initClearTable()
        self.__experiments = []
        for i in tmp:
            self.addExperiment(i)
            
    def __initClearTable(self):
        self.setData([["","","","",""]])
        headers = ['Name','Description','Number of Trials','Parameters','Remove']
        self.setColumnWidth(0,100)
        self.setColumnWidth(1,400)
        self.setColumnWidth(2,130)
        self.setColumnWidth(3,100)
        self.setColumnWidth(4,100)
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalHeaderLabels(headers)
        self.__experiments = []
                  
    def __mkRow(self,params):
        experiment = params.extras
        return [experiment.name,experiment.desc,experiment.numTrials]
    
    
    
    @property
    def experiments(self):
        return self.__experiments
    
    def __len__(self):
        return len(self.experiments)

        
    @property
    def numRows(self):
        return len(self.experiments)
    
class TableViewWidget(GraphicsLayoutWidget):
    """Wraps a custom QtWidget to make a experiment table for setting up batch runs."""
    def __init__(self):
        GraphicsLayoutWidget.__init__(self)
        uic.loadUi(tableUIFile,self)
        self._initTable()

    def _initTable(self):
        self.table = ExperimentQueueTable(self.scrollAreaWidgetContents,editable = False)
    
    def addExperiment(self,*args,**kwargs):
        self.table.addExperiment(*args,**kwargs)

    def updateExperiment(self,*args,**kwargs):
        self.table.updateExperiment(*args,**kwargs)

    def clearTable(self):
        self.table.clearTable()
        

    @property
    def experiments(self):
        return self.table.experiments
    
    def _buildObjectHelper(self):
        try:
            ret = {}
            inputUnit = self.unitLabel_6.text()
            ret['name'] = self.experimentNameEntry.text()
            ret['desc'] = self.experimentDescEntry.toPlainText()
            ret['numTrials'] = self.trialSpinBox.value()
            ret['varianceStr'] = self.varianceTextArea.toPlainText()
            ret['datasets'] = {}
            if self.enableLightCurve.isChecked():
                ret['datasets']['lightcurve'] = {}
                ret['datasets']['lightcurve']['resolution'] = self.dataPointSpinBox.value()
                ret['datasets']['lightcurve']['pstart'] =self.vectorFromQString(self.quasarPathStart.text(),unit=inputUnit)
                ret['datasets']['lightcurve']['pend'] = self.vectorFromQString(self.quasarPathEnd.text(),unit=inputUnit)
            if self.enableMagMap.isChecked():
                ret['datasets']['magmap'] = {}
                ret['datasets']['magmap']['magmapdims'] = self.vectorFromQString(self.magMapDimEntry.text(),unit=inputUnit)
                ret['datasets']['magmap']['magmapres'] = self.vectorFromQString(self.magMapResolutionEntry.text(),None)
            if self.queueSaveStarfield.isChecked():
                ret['datasets']['starfield'] = True
            else:
                ret['datasets']['starfield'] = False
            return ret
        except:
            return "PARSE_ERROR"
        
    def _bindFieldsHelper(self,obj):
        from app.parameters.ExperimentParams import LightCurveParameters, \
        MagMapParameters, StarFieldData, ExperimentParams
        if obj.extras:
            if isinstance(obj.extras,ExperimentParams):
                self.enableLightCurve.setChecked(False)
                self.enableMagMap.setChecked(False)
                self.queueSaveStarfield.setChecked(False)
                for i in obj.extras.desiredResults:
                    if isinstance(i , MagMapParameters):
                        self.enableMagMap.setChecked(True)
                        self.magMapResolutionEntry.setText(i.resolution.asString)
                        dims = i.dimensions.to(self.unitLabel_6.text())
                        self.magMapDimEntry.setText(dims.asString)
                    elif isinstance(i , LightCurveParameters):
                        self.enableLightCurve.setChecked(True)
                        unit = self.unitLabel_3.text()
                        start = i.pathStart.to(unit)
                        end = i.pathEnd.to(unit)
                        self.quasarPathStart.setText(start.asString)
                        self.quasarPathEnd.setText(end.asString)
                        self.dataPointSpinBox.setValue(int(i.resolution))
                    elif isinstance(i, StarFieldData):
                        self.queueSaveStarfield.setChecked(True)
                self.experimentNameEntry.setText(obj.extras.name)
                self.experimentDescEntry.setPlainText(obj.extras.description)
                self.trialSpinBox.setValue(obj.extras.numTrials)
                self.varianceTextArea.document().setPlainText(obj.extras.trialVarianceFunction)
                
    def vectorFromQString(self, string,unit = None):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.

        """
        x, y = (string.strip('()')).split(',')
        if ' ' in y:
            y = y.split(' ')[0]
        return Vector2D(float(x), float(y),unit)
    
    

    
class TableView(View):
    
    _send_extras = pyqtSignal(object)
    _sendTable = pyqtSignal(object)
    
    def __init__(self):
        View.__init__(self)
        self.widget = TableViewWidget()
        self.addWidget(self.widget)
        self.addSignals(set_input_units = self._send_extras,
                        cancel_queue_edit = self.widget.queueEditCancelButton.clicked,
                        save_table = self.widget.tableSaveButton.clicked,
                        clear_table = self.widget.clearTableButton.clicked,
                        editing_params = self.widget.table.editingSignal,
                        send_extras = self._send_extras,
                        send_table = self._sendTable)
        self.signals['clear_table'].connect(self.clearTable)
        self.widget.addToQueueButton.clicked.connect(self.send_input)
        
    def send_input(self):
        extras = self.widget._buildObjectHelper()
        self.signals['send_extras'].emit(extras)
        
    def addExperiment(self,parameters, index):
        if index == -1:
            return self.widget.addExperiment(parameters)
        else:
            self.updateExperiment(parameters,index)
    
    def updateExperiment(self,*args,**kwargs):
        return self.widget.updateExperiment(*args,**kwargs)
    
    def set_input_units(self,unitString):
        print(unitString)
#         self.widget.unitLabel_3.setText(unitString)
#         self.widget.unitLabel_4.setText(unitString)
#         self.widget.unitLabel_6.setText(unitString)

    def update_slot(self,parameters):
        self.widget._bindFieldsHelper(parameters)
    
    def clearTable(self):
        return self.widget.clearTable()
    
    def clear(self):
        self.clearTable()
    
    def sendTable(self):
        table = self.experiments
        self.signals['send_table'].emit(table)
    
    @property
    def experiments(self):
        return self.widget.experiments