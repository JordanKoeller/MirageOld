'''
Created on Jun 1, 2017

@author: jkoeller
'''
# from PyQt5.Qt import QHeaderView
# from PyQt5.QtCore import Qt




from PyQt5 import QtCore

from Controllers import GUIController
from Controllers.FileManagers import QueueFileManager
from Controllers.Threads.QueueThread import QueueThread
from Models.ExperimentQueue.ExperimentQueueTable import ExperimentQueueTable
from Models.Parameters.ExperimentParams import ExperimentParams, ResultTypes
from Calculator.ExperimentResultCalculator import varyTrial

def _queueExtrasBuilder(view,parameters):
    name = view.experimentNameEntry.text()
    desc = view.experimentDescEntry.toPlainText()
    numTrials = view.trialSpinBox.value()
    resolution = view.dataPointSpinBox.value()
    varianceStr = view.varianceTextArea.toPlainText()
    datasets = []
    if view.lightCurveCheckBox.isChecked():
        datasets.append(ResultTypes.LIGHT_CURVE)
    if view.magMapCheckBox.isChecked():
        datasets.append(ResultTypes.MAGMAP)
    if view.starFieldCheckBox.isChecked():
        datasets.append(ResultTypes.STARFIELD)
    pstart =view.vectorFromQString(view.quasarPathStart.text(),False,False,'arcsec')
    pend = view.vectorFromQString(view.quasarPathEnd.text(),False,False,'arcsec')
    extras = ExperimentParams(name=name,description=desc,numTrials=numTrials,trialVariance=varianceStr,pathStart = pstart,pathEnd = pend, resolution = resolution,desiredResults=datasets)
    parameters.extras = extras
    try:
        varyTrial(parameters,0)
    except:
        raise AttributeError

def _queueExtrasBinder(view,obj):
    if obj.extras:
        if isinstance(obj.extras,ExperimentParams):
            start = obj.extras.pathStart.to('arcsec')
            end = obj.extras.pathEnd.to('arcsec')
            view.experimentNameEntry.setText(obj.extras.name)
            view.experimentDescEntry.setPlainText(obj.extras.description)
            view.quasarPathStart.setText("(" + str(start.y) + "," + str(start.x) + ")")
            view.quasarPathEnd.setText("(" + str(end.y) + "," + str(end.x) + ")")
            view.trialSpinBox.setValue(obj.extras.numTrials)

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
        self.editing = -1
        self.__initTable()
#         self.__initConsole()
        
    
        
    def __initTable(self):
        tableSignal = self.view.signals['editExpt']
        self.table = ExperimentQueueTable(tableSignal,self.view.groupBox_5,editable = False)
        self.view.verticalLayout_8.insertWidget(1,self.table)
        self.view.queueStartButton.clicked.connect(self.runExperiments)
        self.view.queueEditCancelButton.clicked.connect(self.cancelEdit)
        self.view.queueEditCancelButton.setEnabled(False)
    
    
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
            
            
    def cancelEdit(self):
        self.view.queueEditCancelButton.setEnabled(False)
        self.view.addToQueueButton.setText("Add to Queue")
        self.editing = -1
        
        
        
#     def buildParameters(self):
#         try:
#             regParams = self.view.parametersController.buildParameters()
#             name = self.view.experimentNameEntry.text()
#             desc = self.view.experimentDescEntry.toPlainText()
#             numTrials = self.view.trialSpinBox.value()
#             resolution = self.view.dataPointSpinBox.value()
#             varianceStr = self.view.varianceTextArea.toPlainText()
#             datasets = []
#             if self.view.lightCurveCheckBox.isChecked():
#                 datasets.append(ResultTypes.LIGHT_CURVE)
#             if self.view.magMapCheckBox.isChecked():
#                 datasets.append(ResultTypes.MAGMAP)
#             if self.view.starFieldCheckBox.isChecked():
#                 datasets.append(ResultTypes.STARFIELD)
#             pstart = self.view.vectorFromQString(self.view.quasarPathStart.text(),False,False,'arcsec')
#             pend = self.view.vectorFromQString(self.view.quasarPathEnd.text(),False,False,'arcsec')
#             extras = ExperimentParams(name=name,description=desc,numTrials=numTrials,trialVariance=varianceStr,pathStart = pstart,pathEnd = pend, resolution = resolution,desiredResults=datasets)
#             regParams.extras = extras
#             return regParams
#         except:
#             self.view.signals['progressLabel'].emit("Error. Input could not be parsed to numbers.")
#             return None
        
    def runExperiments(self):
        fileRunner = QueueFileManager(self.view.signals)
        experiments = self.table.experiments
        runner = QueueThread(self.view.signals,experiments,fileRunner)
        runner.run()
        

    def hide(self):
        self.view.queueFrame.setHidden(True)
        self.view.queueBox.setHidden(True)