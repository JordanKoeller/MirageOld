from PyQt5 import QtCore, QtGui

from .GUIController import GUIController
from .Threads.MagMapTracerThread import MagMapTracerThread
from .FileManagers.FITSFileManager import FITSFileManager
from .FileManagers.VisualizationFileManager import VisualizationFileManager
from .FileManagers.ParametersFileManager import ParametersFileManager
from .FileManagers.MediaFileManager import MediaFileManager
from ..Models.Model import Model
from ..Views.GUI.MagMapTracerView import MagMapTracerView
from ..Utility.NullSignal import NullSignal

import numpy as np


class MagMapTracerController(GUIController):
    '''
    classdocs
    '''
    tracer_signal = QtCore.pyqtSignal(object)
    update_view_signal = QtCore.pyqtSignal(object,object,object)

    def __init__(self, view):
        '''
        Constructor
        '''
        GUIController.__init__(self, view, None, None)
        view.addSignals(tracerUpdate=self.tracer_signal,tracerView=self.update_view_signal)
        self.playToggle = False
        self.thread = None
        self.enabled = True
        self.view.pauseButton.clicked.connect(self.pause)
        self.view.resetButton.clicked.connect(self.restart)
        self.view.playButton.clicked.connect(self.simImage)
        self.view.playPauseAction.triggered.connect(self.togglePlaying)
        self.view.resetAction.triggered.connect(self.restart)
        self.view.displayQuasar.clicked.connect(self.drawQuasarHelper)
        self.view.displayGalaxy.clicked.connect(self.drawGalaxyHelper)
        self.view.record_button.triggered.connect(self.record)
        self.view.signals['paramLabel'].connect(self.qPoslabel_slot)
        self.parametersController = self.view.parametersController
        self.fileManager = MediaFileManager(self.view.signals)
        self.__initView()

    def __initView(self):
        self.tracerView = MagMapTracerView(None, self.view.signals['imageCanvas'], self.view.signals['curveCanvas'], self.tracer_signal,self.update_view_signal)
        self.view.verticalLayout.insertWidget(0, self.tracerView.view)
        self.tracerView.hasUpdated.connect(self.fileManager.sendFrame)
        self.initialize()
        
        
    def togglePlaying(self):
        if self.playToggle:
            self.playToggle = False
            self.pause()
        else:
            self.playToggle = True
            self.simImage()
        

    def show(self):
        self.view.tracerFrame.setHidden(False)
        self.view.regenerateStars.setEnabled(False)
        self.view.visualizationBox.setHidden(False)
        self.enabled = True
        
    def hide(self):
        self.view.tracerFrame.setHidden(True)
        self.view.regenerateStars.setEnabled(True)
        self.view.visualizationBox.setHidden(True)
        self.enabled = False
        
    def drawQuasarHelper(self):
        """Interface for updating an animation in real time of whether or not to draw the physical location of the quasar to the screen as a guide."""
        Model.parameters.showQuasar = self.view.displayQuasar.isChecked()

    def drawGalaxyHelper(self):
        """
        Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
        """
        Model.parameters.showGalaxy = self.view.displayGalaxy.isChecked()
        

    def simImage(self):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        if self.enabled:
            self.playToggle = True
            pixels = self.tracerView.getROI()
            self.thread = MagMapTracerThread(self.view.signals, pixels)
            self.thread.start()

    def record(self):
        """Calling this method will configure the system to save each frame of an animation, for compiling to a video that can be saved."""
        if self.enabled:
            self.fileManager.recording = True
            self.simImage()

    def pause(self):
        if self.enabled:
            self.playToggle = False
            self.thread.pause()

    def restart(self):
        """Returns the system to its t=0 configuration. If the system was configured to record, will automatically prompt the user for a file name,
        render and save the video."""
        if self.enabled:
            self.playToggle = False
            self.thread.restart()
            self.fileManager.write()
        
    def initialize(self):
        paramsLoader = ParametersFileManager(self.view.signals)
        params = paramsLoader.read()
        magmap = self.fileManager.read()
        array = np.asarray(magmap)
        self.tracerView.setMagMap(array)
        Model.updateParameters(params)

    
    def qPoslabel_slot(self, pos):
        self.view.sourcePosLabel.setText(pos)
# 
