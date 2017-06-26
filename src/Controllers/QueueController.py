'''
Created on Jun 1, 2017

@author: jkoeller
'''
# from PyQt5.Qt import QHeaderView
# from PyQt5.QtCore import Qt




from PyQt5 import QtCore

from Calculator.ExperimentResultCalculator import varyTrial
from Controllers import GUIController
from Controllers.FileManagers import QueueFileManager
from Controllers.Threads.QueueThread import QueueThread
from Models.ExperimentQueue.ExperimentQueueTable import ExperimentQueueTable
from Models.Parameters.ExperimentParams import ExperimentParams, ResultTypes
from Models.Parameters.MagMapParameters import MagMapParameters
from Models.Parameters.LightCurveParameters import LightCurveParameters

def _queueExtrasBuilder(view,parameters):
    name = view.experimentNameEntry.text()
    desc = view.experimentDescEntry.toPlainText()
    numTrials = view.trialSpinBox.value()
    varianceStr = view.varianceTextArea.toPlainText()
    datasets = []
    if view.enableLightCurve.isChecked():
        
        resolution = view.dataPointSpinBox.value()
        pstart =view.vectorFromQString(view.quasarPathStart.text(),unit='arcsec')
        pend = view.vectorFromQString(view.quasarPathEnd.text(),unit='arcsec')
        lcparams = LightCurveParameters(pstart,pend,resolution)
        datasets.append(lcparams)
    if view.enableMagMap.isChecked():
        magmapcenter = view.vectorFromQString(view.magMapCenterEntry.text(),unit='arcsec')
        magmapdims = view.vectorFromQString(view.magMapDimEntry.text(),unit='arcsec')
        magmapres = view.vectorFromQString(view.magMapResolutionEntry.text(),None)
        magmapparams = MagMapParameters(magmapcenter,magmapdims,magmapres)
        datasets.append(magmapparams)
#     if view.starFieldCheckBox.isChecked():
#         datasets.append(ResultTypes.STARFIELD)
    extras = ExperimentParams(name=name,description=desc,numTrials=numTrials,trialVariance=varianceStr,resultParams=datasets)
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
        self.view.enableLightCurve.clicked.connect(self.toggleLightCurveEntry)
        self.view.enableMagMap.clicked.connect(self.toggleMagMapEntry)
        self.toggleLightCurveEntry()
        self.toggleMagMapEntry()
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
            
            
    def cancelEdit(self):
        self.view.queueEditCancelButton.setEnabled(False)
        self.view.addToQueueButton.setText("Add to Queue")
        self.editing = -1
        
    def toggleLightCurveEntry(self):
        if self.view.enableLightCurve.isChecked():
            self.view.quasarPathStart.setEnabled(True)
            self.view.quasarPathEnd.setEnabled(True)
            self.view.dataPointSpinBox.setEnabled(True)
        else:
            self.view.quasarPathEnd.setEnabled(False)
            self.view.quasarPathStart.setEnabled(False)
            self.view.dataPointSpinBox.setEnabled(False)
    
    def toggleMagMapEntry(self):
        if self.view.enableMagMap.isChecked():
            self.view.magMapCenterEntry.setEnabled(True)
            self.view.magMapDimEntry.setEnabled(True)
            self.view.magMapResolutionEntry.setEnabled(True)
        else:
            self.view.magMapCenterEntry.setEnabled(False)
            self.view.magMapDimEntry.setEnabled(False)
            self.view.magMapResolutionEntry.setEnabled(False)
        
    def runExperiments(self):
        fileRunner = QueueFileManager(self.view.signals)
        experiments = self.table.experiments
        runner = QueueThread(self.view.signals,experiments,fileRunner)
        runner.run()
        

    def hide(self):
        self.view.queueFrame.setHidden(True)
        self.view.queueBox.setHidden(True)