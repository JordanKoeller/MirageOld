'''
Created on May 31, 2017

@author: jkoeller
'''

import sys

from PyQt5 import QtWidgets, uic, QtCore

from ...Controllers.ParametersController import ParametersController
from ...Controllers.VisualizationController import VisualizationController
from ...Controllers.QueueController import QueueController
from ...Utility import Vector2D
from PyQt5.QtWidgets import QProgressDialog
from ...Utility.SignalRepo import SignalRepo


class GUIManager(QtWidgets.QMainWindow,SignalRepo):
    '''
    classdocs
    '''
    progressBar_signal = QtCore.pyqtSignal(int)
    progressDialog_signal = QtCore.pyqtSignal(int,int,str)
    progressLabel_signal = QtCore.pyqtSignal(str)
    progressBarMax_signal = QtCore.pyqtSignal(int)
    

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(GUIManager, self).__init__(parent)
        uic.loadUi('Resources/gui.ui', self)
        self.addSignals(progressBar = self.progressBar_signal,
                        progressLabel = self.progressLabel_signal,
                        progressBarMax = self.progressBarMax_signal,
                        progressDialog = self.progressDialog_signal
                        )
        self.signals['progressBar'].connect(self.progressBar.setValue)
        self.signals['progressLabel'].connect(self.progressLabel.setText)
        self.signals['progressBarMax'].connect(self.progressBar.setMaximum)
        self.signals['progressDialog'].connect(self.startProgressDialog)
        self.visualizationFrame.setHidden(True)
        self.visualizationBox.setHidden(True)
        self.queueFrame.setHidden(True)
        self.queueBox.setHidden(True)
        self.parametersController = ParametersController(self)
        self.visualPerspective = VisualizationController(self)
        self.queuePerspective = QueueController(self)
        self.magTracingPerspective = None
        self.perspective = None
        self.switchToVisualizing()
        self.progressBar.setValue(0)
        self.shutdown.triggered.connect(sys.exit)
        self.visualizerViewSelector.triggered.connect(self.switchToVisualizing)
        self.queueViewSelector.triggered.connect(self.switchToQueue)
    
    def __switchToPerspective(self,perspective):
        if self.perspective:
            self.perspective.hide()
        self.perspective = perspective
        self.perspective.show()
        
    def switchToVisualizing(self):
        if self.visualPerspective:
            self.__switchToPerspective(self.visualPerspective)
        else:
            self.__switchToPerspective(VisualizationController(self))
    
    def switchToQueue(self):
        if self.queuePerspective:
            self.__switchToPerspective(self.queuePerspective)
        else:
            self.__switchToPerspective(QueueController(self))
    
    def hideParameters(self):
        self.parametersController.hide()
            
    def showParameters(self):
        self.parametersController.show()
            
    def bindFields(self,parameters):
        self.parametersController.bindFields(parameters,self.perspective.extrasBinder)
        
    def buildParameters(self):
        return self.parametersController.buildParameters(self.perspective.extrasBuilder)

            
            
    def vectorFromQString(self, string,unit = None):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.

        Parameters:
            reverse_y : Boolean
                specify whether or not to negate y-coordinates to convert a conventional coordinate system of positive y in the up direction to
                positive y in the down direction as used by graphics libraries. Default False

            transpose : Boolean
                Specify whether or not to flip x and y coordinates. In other words, return a Vector2D of (y,x) rather than (x,y). Default True
        """
        x, y = (string.strip('()')).split(',')
        if ' ' in y:
            y = y.split(' ')[0]
        return Vector2D(float(x), float(y),unit)

    

    def startProgressDialog(self,minimum,maximum,message):
        self.dialog = QProgressDialog(message,'Ok',minimum,maximum)
        self.progressBar_signal.connect(self.dialog.setValue)
