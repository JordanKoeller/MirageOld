'''
Created on Jun 1, 2017

@author: jkoeller
'''
# from PyQt5.Qt import QHeaderView
# from PyQt5.QtCore import Qt




from PyQt5 import QtCore

from ..Calculator.ExperimentResultCalculator import varyTrial
from .GUIController import GUIController
from .FileManagers.QueueFileManager import QueueFileManager
from .Threads.QueueThread import QueueThread
from ..Models.ExperimentQueue.ExperimentQueueTable import ExperimentQueueTable
from ..Models.Parameters.ExperimentParams import ExperimentParams, ResultTypes
from ..Models.Parameters.MagMapParameters import MagMapParameters
from ..Models.Parameters.LightCurveParameters import LightCurveParameters
from ..Models.Parameters.StarFieldData import StarFieldData
from ..Models.ParametersError import ParametersError
from ..Models.Model import Model
from ..Controllers.FileManagers.TableFileManager import TableFileManager
from ..Utility import Vector2D

def _queueExtrasBuilder(view,parameters,inputUnit):
    name = view.experimentNameEntry.text()
    desc = view.experimentDescEntry.toPlainText()
    numTrials = view.trialSpinBox.value()
    varianceStr = view.varianceTextArea.toPlainText()
    datasets = []
    if view.enableLightCurve.isChecked():
        resolution = view.dataPointSpinBox.value()
        pstart =view.vectorFromQString(view.quasarPathStart.text(),unit=inputUnit)
        pend = view.vectorFromQString(view.quasarPathEnd.text(),unit=inputUnit)
        lcparams = LightCurveParameters(pstart,pend,resolution)
        datasets.append(lcparams)
    if view.enableMagMap.isChecked():
        magmapdims = view.vectorFromQString(view.magMapDimEntry.text(),unit=inputUnit)
        magmapres = view.vectorFromQString(view.magMapResolutionEntry.text(),None)
        magmapcenter = Model.engine.getCenterCoords(parameters)
        magmapparams = MagMapParameters(magmapcenter,magmapdims,magmapres)
        datasets.append(magmapparams)
    if view.queueSaveStarfield.isChecked():
        datasets.append(StarFieldData())
    extras = ExperimentParams(name=name,description=desc,numTrials=numTrials,trialVariance=varianceStr,resultParams=datasets)
    parameters.extras = extras
    try:
        varyTrial(parameters,0)
    except ParametersError as e:
        raise ParametersError(e.value)
    except:
        raise SyntaxError("Syntax error found in trial variance code block.")

def _queueExtrasBinder(view,obj):
    if obj.extras:
        if isinstance(obj.extras,ExperimentParams):
            view.enableLightCurve.setChecked(False)
            view.enableMagMap.setChecked(False)
            view.queueSaveStarfield.setChecked(False)
            for i in obj.extras.desiredResults:
                if isinstance(i , MagMapParameters):
                    view.enableMagMap.setChecked(True)
                    view.magMapResolutionEntry.setText("("+str(i.resolution.x)+","+str(i.resolution.y)+")")
                    dims = i.dimensions.to(view.unitLabel_6.text())
                    view.magMapDimEntry.setText("("+str(dims.x)+","+str(dims.y)+")")
                elif isinstance(i , LightCurveParameters):
                    view.enableLightCurve.setChecked(True)
                    unit = view.unitLabel_3.text()
                    start = i.pathStart.to(unit)
                    end = i.pathEnd.to(unit)
                    view.quasarPathStart.setText("(" + str(start.y) + "," + str(start.x) + ")")
                    view.quasarPathEnd.setText("(" + str(end.y) + "," + str(end.x) + ")")
                    view.dataPointSpinBox.setValue(int(i.resolution))
                elif isinstance(i, StarFieldData):
                    view.queueSaveStarfield.setChecked(True)
            view.experimentNameEntry.setText(obj.extras.name)
            view.experimentDescEntry.setPlainText(obj.extras.description)
            view.trialSpinBox.setValue(obj.extras.numTrials)
            view.varianceTextArea.document().setPlainText(obj.extras.trialVarianceFunction)

class QueueController(GUIController):
    '''
    classdocs
    '''
    
    editExpt_signal = QtCore.pyqtSignal(object,int)

    def __init__(self, view):
        '''
        Constructor
        '''
        GUIController.__init__(self,view,_queueExtrasBinder,_queueExtrasBuilder)
        self.view.addSignals(editExpt = self.editExpt_signal)
        self.view.signals['editExpt'].connect(self.editParams)
        self.view.addToQueueButton.clicked.connect(self.addToQueue)
        self.view.enableLightCurve.toggled.connect(self.toggleLightCurveEntry)
        self.view.enableMagMap.toggled.connect(self.toggleMagMapEntry)
        self.view.saveTableAction.triggered.connect(self.saveTable)
        self.view.loadTableAction.triggered.connect(self.loadTable)
        self.tableFileManager = TableFileManager(self.view.signals)
        self.toggleLightCurveEntry(False)
        self.toggleMagMapEntry(False)
        self.editing = -1
        self.runner = QueueThread(self.view.signals)
        self.__initTable()
        
    
        
    def __initTable(self):
        tableSignal = self.view.signals['editExpt']
        self.table = ExperimentQueueTable(tableSignal,self.view.groupBox_5,editable = False)
        self.view.verticalLayout_8.insertWidget(0,self.table)
        self.view.queueStartButton.clicked.connect(self.runExperiments)
        self.view.queueEditCancelButton.clicked.connect(self.cancelEdit)
        self.view.queueEditCancelButton.setEnabled(False)
        self.view.clearTableButton.clicked.connect(self.table.clearTable)
    
    
    def show(self):
        self.view.queueFrame.setHidden(False)
        self.view.queueBox.setHidden(False)
        
    def editParams(self,params,row):
        self.view.signals['paramSetter'].emit(params)
        self.view.bindFields(params)
        self.editing = row
        self.view.queueEditCancelButton.setEnabled(True)
        self.view.addToQueueButton.setText("Update")
             
                
    def addToQueue(self):
        exp = self.view.buildParameters()
        if exp:
            if self.editing == -1:
                self.table.addExperiment(exp)
            else:
                self.table.updateExperiment(exp,self.editing)
                self.cancelEdit()
                
    def saveTable(self):
        tableFull = self.table.experiments
        self.tableFileManager.write(tableFull)
        
    def loadTable(self):
        tableFull = self.tableFileManager.read()
        if tableFull:
            self.table.clearTable()
            for i in tableFull:
                self.table.addExperiment(i)
            
            
    def cancelEdit(self):
        self.view.queueEditCancelButton.setEnabled(False)
        self.view.addToQueueButton.setText("Add to Queue")
        self.editing = -1
        
    def toggleLightCurveEntry(self,on):
        if on:
            self.view.quasarPathStart.setEnabled(True)
            self.view.quasarPathEnd.setEnabled(True)
            self.view.dataPointSpinBox.setEnabled(True)
        else:
            self.view.quasarPathEnd.setEnabled(False)
            self.view.quasarPathStart.setEnabled(False)
            self.view.dataPointSpinBox.setEnabled(False)
    
    def toggleMagMapEntry(self,on):
        if on:
            self.view.magMapDimEntry.setEnabled(True)
            self.view.magMapResolutionEntry.setEnabled(True)
        else:
            self.view.magMapDimEntry.setEnabled(False)
            self.view.magMapResolutionEntry.setEnabled(False)
        
    def runExperiments(self):
        fileRunner = QueueFileManager(self.view.signals)
        if fileRunner.madeDirectory:
            experiments = self.table.experiments
            self.runner.bindExperiments(experiments,fileRunner)
            self.runner.start()
        

    def hide(self):
        self.view.queueFrame.setHidden(True)
        self.view.queueBox.setHidden(True)