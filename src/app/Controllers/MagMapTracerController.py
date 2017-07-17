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
    tracer_updated = QtCore.pyqtSignal(str)
    run_done = QtCore.pyqtSignal(str)

    def __init__(self, view):
        '''
        Constructor
        '''
        GUIController.__init__(self, view, None, None)
        view.addSignals(tracerUpdate=self.tracer_signal,tracerView=self.update_view_signal,tracerUpdated=self.tracer_updated,tracerDone = self.run_done)
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
        self.view.signals['tracerUpdated'].connect(self.sendOffFrame)
        self.view.signals['tracerDone'].connect(self.writeMov)
        self.parametersController = self.view.parametersController
        self.fileManager = MediaFileManager(self.view.signals)
        self.__initView()

    def __initView(self):
        self.tracerView = MagMapTracerView(self.view,self.update_view_signal)
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
        # self.view.tracerFrame.setHidden(False)
        self.view.magTracerFrame.setHidden(False)
        self.view.regenerateStars.setEnabled(False)
        self.view.visualizationBox.setHidden(False)
        self.enabled = True
        
    def hide(self):
        # self.view.tracerFrame.setHidden(True)
        self.view.magTracerFrame.setHidden(True)
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
        

    def simImage(self,recording=False):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        if self.enabled:
            if recording:
                self.tracerView.setUpdatesEnabled(False)
            else:
                self.tracerView.setUpdatesEnabled(True)
            # self.tracerView.setUpdatesEnabled(not recording)
            self.playToggle = True
            pixels = self.tracerView.getROI()
            self.thread = MagMapTracerThread(self.view.signals, pixels,recording=recording)
            self.thread.start()

    def record(self):
        """Calling this method will configure the system to save each frame of an animation, for compiling to a video that can be saved."""
        if self.enabled:
            self.simImage(recording=True)

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
            self.fileManager.cancelRecording()
            
    def writeMov(self):
        self.tracerView.setUpdatesEnabled(True)
        self.fileManager.write()
            
    def sendOffFrame(self,filler):
        frame = self.tracerView.getFrame()
        self.fileManager.sendFrame(frame)
        
    def initialize(self):
        paramsLoader = ParametersFileManager(self.view.signals)
        params = paramsLoader.read()
        magmap = self.fileManager.read()
        if not params or not magmap:
            return False
        self.view.bindFields(params)
        array = np.asarray(magmap)[:,:,0:3]
        self.tracerView.setMagMap(array)
        Model.updateParameters(params)

    
    def qPoslabel_slot(self, pos):
        self.view.sourcePosLabel.setText(pos)
# 
