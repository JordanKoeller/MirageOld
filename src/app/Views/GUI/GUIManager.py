'''
Created on May 31, 2017

@author: jkoeller
'''

import sys

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QProgressDialog

from app.Controllers.VisualizationController import VisualizationController
import factory

from ... import mainUIFile
from ...Controllers.QueueController import QueueController
from ...Utility import Vector2D
from ...Utility.SignalRepo import SignalRepo


# from ...Controllers.ParametersController import ParametersController
# from ...Controllers.VisualizationController import VisualizationController
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
        uic.loadUi(mainUIFile, self)
        self.addSignals(progressBar = self.progressBar_signal,
                        progressLabel = self.progressLabel_signal,
                        progressBarMax = self.progressBarMax_signal,
                        progressDialog = self.progressDialog_signal
                        )
        self.signals['progressBar'].connect(self.progressBar.setValue)
        self.signals['progressLabel'].connect(self.progressLabel.setText)
        self.signals['progressBarMax'].connect(self.progressBar.setMaximum)
        self.signals['progressDialog'].connect(self.startProgressDialog)
        self.parametersController = factory._ParametersControllerFactory(self)
        self.visController = VisualizationController(self)
        self.isPlaying = False
        # self.visController.show()
        self.magTracingPerspective = None
        self.perspective = None
        self.progressBar.setValue(0)
        self.shutdown.triggered.connect(sys.exit)
        self.initStatusBar()
    # def togglePlaying(self):
    #     if self.isPlaying:
    #         self.isPlaying = False
    #         self.thread.pause()
    #     else:
    #         self.isPlaying = True


    # def reset(self):


    def hideParameters(self):
        self.parametersController.hide()
            
    def showParameters(self):
        self.parametersController.show()
            
    def bindFields(self,parameters):
        self.parametersController.bindFields(parameters,self.perspective.extrasBinder)
        
    def buildParameters(self):
        return self.parametersController.buildParameters(self.perspective.extrasBuilder)

    def initStatusBar(self):
        playButton = QtWidgets.QPushButton("Play/Pause")
        # playButton.clicked.connect(self.togglePlaying)
        resetButton = QtWidgets.QPushButton("Reset")
        # resetButton.clicked.connect(self.reset)
        self.statusBar.addWidget(playButton)
        self.statusBar.addWidget(resetButton)

            
            
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
        
        
