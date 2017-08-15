'''
Created on Jun 1, 2017

@author: jkoeller
'''

from PyQt5 import QtCore

from ..Calculator.ExperimentResultCalculator import varyTrial
from .GUIController import GUIController
from .FileManagers.QueueFileManager import QueueFileManager
from .Threads.QueueThread import QueueThread
from ..Views.ExperimentQueueTable import ExperimentQueueTable
from ..Models.Parameters.ExperimentParams import ExperimentParams
from ..Models.Parameters.MagMapParameters import MagMapParameters
from ..Models.Parameters.LightCurveParameters import LightCurveParameters
from ..Models.Parameters.StarFieldData import StarFieldData
from ..Utility.ParametersError import ParametersError
from app.Models import ModelImpl
from ..Controllers.FileManagerImpl import TableFileWriter, TableFileReader
from .ParametersController import ParametersController
from .UserInputParser import UserInputParser

class QueueController(UserInputParser,GUIController):
    '''
    classdocs
    '''
    

    def __init__(self, tableview=None, parameterscontroller=None):
        '''
        Constructor
        '''
        GUIController.__init__(self,None,None,None)
        UserInputParser.__init__(self,tableview)
        self.view = tableview
        self.parametersView = parameterscontroller.view
        self.parametersController = parameterscontroller
        self.parametersView.scaleUnitOption.currentTextChanged.connect(self.setUnits)
        self.view.addToQueueButton.clicked.connect(self.addToQueue)
        self.view.queueEditCancelButton.clicked.connect(self.cancelEdit)
        self.view.queueEditCancelButton.setEnabled(False)
        self.view.tableSaveButton.clicked.connect(self.saveTable)
        self.view.clearTableButton.clicked.connect(self.view.clearTable)
        self.editing = -1
        self.view.table.editingSignal.connect(self.editParams)

        # self.runner = QueueThread(self.view.signals)
        
    
        
    def editParams(self,params,row):
        # self.view.signals['paramSetter'].emit(params)
        self.parametersController.bindFields(params)
        self.bindFields(params)
        self.editing = row
        self.view.queueEditCancelButton.setEnabled(True)
        self.view.addToQueueButton.setText("Update")
             
                
    def addToQueue(self):
        exp = self.parametersController.buildObject()
        exp = self.buildObject(exp)
        if exp:
            if self.editing == -1:
                self.view.addExperiment(exp)
            else:
                self.view.updateExperiment(exp,self.editing)
                self.cancelEdit()
                
    def saveTable(self):
        tableFull = self.view.experiments
        tableFileManager = TableFileWriter()
        tableFileManager.open()
        tableFileManager.write(tableFull)
        
    def loadTable(self):
        tableFileManager = TableFileReader()
        tableFileManager.open()
        tableFull = tableFileManager.load()
        if tableFull:
            self.view.clearTable()
            for i in tableFull:
                self.view.addExperiment(i)
            
            
    def cancelEdit(self):
        self.view.queueEditCancelButton.setEnabled(False)
        self.view.addToQueueButton.setText("Add to Queue")
        self.editing = -1
        

    def setUnits(self,unitString):
        self.view.unitLabel_3.setText(unitString)
        self.view.unitLabel_4.setText(unitString)
        self.view.unitLabel_6.setText(unitString)


    def _buildObjectHelper(self,parameters):
        inputUnit = self.view.unitLabel_6.text()
        name = self.view.experimentNameEntry.text()
        desc = self.view.experimentDescEntry.toPlainText()
        numTrials = self.view.trialSpinBox.value()
        varianceStr = self.view.varianceTextArea.toPlainText()
        datasets = []
        if self.view.enableLightCurve.isChecked():
            resolution = self.view.dataPointSpinBox.value()
            pstart =self.view.vectorFromQString(self.view.quasarPathStart.text(),unit=inputUnit)
            pend = self.view.vectorFromQString(self.view.quasarPathEnd.text(),unit=inputUnit)
            lcparams = LightCurveParameters(pstart,pend,resolution)
            datasets.append(lcparams)
        if self.view.enableMagMap.isChecked():
            magmapdims = self.view.vectorFromQString(self.view.magMapDimEntry.text(),unit=inputUnit)
            magmapres = self.view.vectorFromQString(self.view.magMapResolutionEntry.text(),None)
            magmapcenter = ModelImpl.engine.getCenterCoords(parameters)
            magmapparams = MagMapParameters(magmapcenter,magmapdims,magmapres)
            datasets.append(magmapparams)
        if self.view.queueSaveStarfield.isChecked():
            datasets.append(StarFieldData())
        extras = ExperimentParams(name=name,description=desc,numTrials=numTrials,trialVariance=varianceStr,resultParams=datasets)
        parameters.extras = extras
        try:
            varyTrial(parameters,0)
            return parameters
        except ParametersError as e:
            raise ParametersError(e.value)
        except:
            raise SyntaxError("Syntax error found in trial variance code block.")

    def _bindFieldsHelper(self,obj):
        if obj.extras:
            if isinstance(obj.extras,ExperimentParams):
                self.view.enableLightCurve.setChecked(False)
                self.view.enableMagMap.setChecked(False)
                self.view.queueSaveStarfield.setChecked(False)
                for i in obj.extras.desiredResults:
                    if isinstance(i , MagMapParameters):
                        self.view.enableMagMap.setChecked(True)
                        self.view.magMapResolutionEntry.setText(i.resolution.asString)
                        dims = i.dimensions.to(view.unitLabel_6.text())
                        self.view.magMapDimEntry.setText(dims.asString)
                    elif isinstance(i , LightCurveParameters):
                        self.view.enableLightCurve.setChecked(True)
                        unit = view.unitLabel_3.text()
                        start = i.pathStart.to(unit)
                        end = i.pathEnd.to(unit)
                        self.view.quasarPathStart.setText(start.asString)
                        self.view.quasarPathEnd.setText(end.asString)
                        self.view.dataPointSpinBox.setValue(int(i.resolution))
                    elif isinstance(i, StarFieldData):
                        self.view.queueSaveStarfield.setChecked(True)
                self.view.experimentNameEntry.setText(obj.extras.name)
                self.view.experimentDescEntry.setPlainText(obj.extras.description)
                self.view.trialSpinBox.setValue(obj.extras.numTrials)
                self.view.varianceTextArea.document().setPlainText(obj.extras.trialVarianceFunction)
