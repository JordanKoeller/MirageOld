'''
Created on Jul 17, 2017

@author: jkoeller
'''
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QMainWindow, QProgressDialog
from ...Utility.SignalRepo import SignalRepo
from ...Controllers.MagMapTracerController import MagMapTracerController
from ...Views.GUI.MagMapTracerView import MagMapTracerView


class GUITracerWindow(QMainWindow,SignalRepo):
    '''
    classdocs
    '''
    progressBar_signal = QtCore.pyqtSignal(int)
    statusBar_signal = QtCore.pyqtSignal(str)
    progressDialog_signal = QtCore.pyqtSignal(int,int,str)
    _setProgress = QtCore.pyqtSignal(int)
    
    def __init__(self, filename=None,trialNum=0):
        '''
        Constructor
        '''
        super(GUITracerWindow,self).__init__()
        uic.loadUi('Resources/TracerGUI/tracerwindow.ui',self)
        self.addSignals(progressDialog = self.progressDialog_signal,
                        progressBar = self.progressBar_signal,
                        progressLabel = self.statusBar_signal)
        self.signals['progressDialog'].connect(self.initProgressDialog)
        self.signals['progressBar'].connect(self.setProgressValue)
        self.signals['progressLabel'].connect(self.showMessage)
        self._counter = 0
        tracerView = MagMapTracerView(self.tracerFrame,self.plotView,self.imgView,self.gradientSelector)
        self.tracerController = MagMapTracerController(self,tracerView,filename)
        
    def showMessage(self,msg,timeout = 5000):
        self.statusBar.showMessage(msg,timeout)
        
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
        