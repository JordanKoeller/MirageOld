'''
Created on Jul 17, 2017

@author: jkoeller
'''
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QMainWindow, QProgressDialog, QLabel

from ...Controllers.MagMapTracerController import MagMapTracerController
from .MagMapTracerView import MagMapTracerView
from .TracerPreferences import PreferencesDialog

from ...Utility.SignalRepo import SignalRepo


class GUITracerWindow(QMainWindow,SignalRepo):
    '''
    classdocs
    '''
    progressBar_signal = QtCore.pyqtSignal(int)
    statusBar_signal = QtCore.pyqtSignal(str)
    progressDialog_signal = QtCore.pyqtSignal(int,int,str)
    _setProgress = QtCore.pyqtSignal(int)
    qPosLabel_signal = QtCore.pyqtSignal(object)
    
    def __init__(self, filename=None,trialNum=0):
        '''
        Constructor
        '''
        super(GUITracerWindow,self).__init__()
        uic.loadUi('Resources/TracerGUI/tracerwindow.ui',self)
        prefs = PreferencesDialog('Resources/TracerGUI/preferencesdialog.ui',self)
        self.addSignals(progressDialog = self.progressDialog_signal,
                        progressBar = self.progressBar_signal,
                        progressLabel = self.statusBar_signal,
                        qPosLabel = self.qPosLabel_signal)
        self.signals['progressDialog'].connect(self.initProgressDialog)
        self.signals['progressBar'].connect(self.setProgressValue)
#         self.signals['progressLabel'].connect(self.showMessage)
        self.signals['qPosLabel'].connect(self.displayQPos)
        self.qPosLabel = QLabel(self.statusBar)
        self.statusBar.addWidget(self.qPosLabel)
        self._counter = 0
        tracerView = MagMapTracerView(self.tracerFrame,self.plotView,self.imgView,self.gradientSelector)
        self.tracerController = MagMapTracerController(self,tracerView,filename,trialNum)
#         print(prefs.exec())
        
    def showMessage(self,msg,timeout = 5000):
        self.statusBar.showMessage(msg,timeout)
            
    def displayQPos(self,pos):
        self.qPosLabel.setText(str(pos))
        
    def initProgressDialog(self,minimum,maximum,msg):
        self._counter = minimum
        self.dialog = QProgressDialog(msg,'Ok',minimum,maximum)
        self.dialog.setModal(False)
        self._setProgress.connect(self.dialog.setValue)
        
    def setProgressValue(self,value=-1):
        def helper():
            if value is -1:
                self._counter += 1
                self.dialog.setValue(value)
            else:
                self.dialog.setValue(value)
                self._counter = value
        