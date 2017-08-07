'''
Created on Jun 1, 2017

@author: jkoeller
'''
# from PyQt5.Qt import QHeaderView
# from PyQt5.QtCore import Qt




# from PyQt5 import QtCore

# from ..Calculator.ExperimentResultCalculator import varyTrial
# from .GUIController import GUIController
# from .FileManagers.QueueFileManager import QueueFileManager
# from .Threads.QueueThread import QueueThread
# from ..Models.ExperimentQueue.ExperimentQueueTable import ExperimentQueueTable
# from ..Models.Parameters.ExperimentParams import ExperimentParams
# from ..Models.Parameters.MagMapParameters import MagMapParameters
# from ..Models.Parameters.LightCurveParameters import LightCurveParameters
# from ..Models.Parameters.StarFieldData import StarFieldData
# from ..Models.ParametersError import ParametersError
# from app.Models import ModelImpl
# from ..Controllers.FileManagers.TableFileManager import TableFileManager

# class QueueController(GUIController):
#     '''
#     classdocs
#     '''
    
#     editExpt_signal = QtCore.pyqtSignal(object,int)

#     def __init__(self, view):
#         '''
#         Constructor
#         '''
#         GUIController.__init__(self,view,_queueExtrasBinder,_queueExtrasBuilder)
#         self.view.addSignals(editExpt = self.editExpt_signal)
#         self.view.signals['editExpt'].connect(self.editParams)
#         self.view.addToQueueButton.clicked.connect(self.addToQueue)
#         self.view.enableLightCurve.toggled.connect(self.toggleLightCurveEntry)
#         self.view.enableMagMap.toggled.connect(self.toggleMagMapEntry)
#         self.view.saveTableAction.triggered.connect(self.saveTable)
#         self.view.loadTableAction.triggered.connect(self.loadTable)
#         self.tableFileManager = TableFileManager(self.view.signals)
#         self.toggleLightCurveEntry(False)
#         self.toggleMagMapEntry(False)
#         self.editing = -1
#         self.runner = QueueThread(self.view.signals)
#         self.__initTable()
        
    
        
#     def __initTable(self):
#         tableSignal = self.view.signals['editExpt']
#         self.table = ExperimentQueueTable(tableSignal,self.view.groupBox_5,editable = False)
#         self.view.verticalLayout_8.insertWidget(0,self.table)
#         self.view.queueStartButton.clicked.connect(self.runExperiments)
#         self.view.queueEditCancelButton.clicked.connect(self.cancelEdit)
#         self.view.queueEditCancelButton.setEnabled(False)
#         self.view.clearTableButton.clicked.connect(self.table.clearTable)
    
    
#     def show(self):
#         self.view.queueFrame.setHidden(False)
#         self.view.queueBox.setHidden(False)
        
#     def editParams(self,params,row):
#         self.view.signals['paramSetter'].emit(params)
#         self.view.bindFields(params)
#         self.editing = row
#         self.view.queueEditCancelButton.setEnabled(True)
#         self.view.addToQueueButton.setText("Update")
             
                
#     def addToQueue(self):
#         exp = self.view.buildParameters()
#         if exp:
#             if self.editing == -1:
#                 self.table.addExperiment(exp)
#             else:
#                 self.table.updateExperiment(exp,self.editing)
#                 self.cancelEdit()
                
#     def saveTable(self):
#         tableFull = self.table.experiments
#         self.tableFileManager.write(tableFull)
        
#     def loadTable(self):
#         tableFull = self.tableFileManager.read()
#         if tableFull:
#             self.table.clearTable()
#             for i in tableFull:
#                 self.table.addExperiment(i)
            
            
#     def cancelEdit(self):
#         self.view.queueEditCancelButton.setEnabled(False)
#         self.view.addToQueueButton.setText("Add to Queue")
#         self.editing = -1
        
#     def toggleLightCurveEntry(self,on):
#         if on:
#             self.view.quasarPathStart.setEnabled(True)
#             self.view.quasarPathEnd.setEnabled(True)
#             self.view.dataPointSpinBox.setEnabled(True)
#         else:
#             self.view.quasarPathEnd.setEnabled(False)
#             self.view.quasarPathStart.setEnabled(False)
#             self.view.dataPointSpinBox.setEnabled(False)
    
#     def toggleMagMapEntry(self,on):
#         if on:
#             self.view.magMapDimEntry.setEnabled(True)
#             self.view.magMapResolutionEntry.setEnabled(True)
#         else:
#             self.view.magMapDimEntry.setEnabled(False)
#             self.view.magMapResolutionEntry.setEnabled(False)
        
#     def runExperiments(self):
#         fileRunner = QueueFileManager(self.view.signals)
#         if fileRunner.madeDirectory:
#             experiments = self.table.experiments
#             self.runner.bindExperiments(experiments,fileRunner)
#             self.runner.start()
        

#     def hide(self):
#         self.view.queueFrame.setHidden(True)
#         self.view.queueBox.setHidden(True)



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
from ..Models.ParametersError import ParametersError
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
