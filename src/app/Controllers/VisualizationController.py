'''
Created on May 31, 2017

@author: jkoeller
'''

from PyQt5 import QtCore

from .GUIController import GUIController
from .Threads.VisualizerThread import VisualizerThread
from .FileManagers.FITSFileManager import FITSFileManager
from .FileManagers.MediaFileManager import MediaFileManager
from ..Models.Model import Model
from ..Views.ViewLayout import ViewLayout
from ..Views.LensedImageView import LensedImageView
from ..Views.LightCurvePlotView import LightCurvePlotView
from . import ControllerFactory


class VisualizationController(GUIController):
    '''
    classdocs
    '''
    imageCanvas_signal = QtCore.pyqtSignal(object)
    curveCanvas_signal = QtCore.pyqtSignal(object, object)


    def __init__(self, view):
        '''
        Constructor
        '''
        GUIController.__init__(self,view,None,None)
        view.addSignals(imageCanvas = self.imageCanvas_signal, curveCanvas = self.curveCanvas_signal)
        self.playToggle = False
        self.enabled = False
        self.thread = VisualizerThread(self.view.signals)
        self.recording = False
        self.view.pauseButton.clicked.connect(self.pause)
        self.view.playButton.clicked.connect(self.simImage)
        self.view.playPauseAction.triggered.connect(self.togglePlaying)
        self.view.resetAction.triggered.connect(self.restart)
        self.view.record_button.triggered.connect(self.record)
        self.views = []
        self.initVisCanvas()
        self.view.signals['paramLabel'].connect(self.qPoslabel_slot)
        self.parametersController = self.view.parametersController
        self.fileManager = MediaFileManager(self.view.signals)

    def togglePlaying(self):
        if self.playToggle:
            self.playToggle = False
            self.pause()
        else:
            self.playToggle = True
            self.simImage()
        
    def initVisCanvas(self):
        layout = ViewLayout(None,None)
        imgCanvas = LensedImageView(None)
        plCanvas = LightCurvePlotView(None)
        self.views.append(imgCanvas)
        self.views.append(plCanvas)
        layout.addView(plCanvas)
        layout.addView(imgCanvas)
        self.view.mainSplitter.addWidget(layout)

    def show(self):
        self.view.visualizationFrame.setHidden(False)
        self.view.visualizationBox.setHidden(False)
        self.enabled = True
        
    def hide(self):
        self.view.visualizationBox.setHidden(True)
        self.view.visualizationFrame.setHidden(True)
        self.enabled = False
        
    # def drawQuasarHelper(self):
    #     """Interface for updating an animation in real time of whether or not to draw the physical location of the quasar to the screen as a guide."""
    #     Model.parameters.showQuasar = self.view.displayQuasar.isChecked()

    # def drawGalaxyHelper(self):
    #     """
    #     Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
    #     """
    #     Model.parameters.showGalaxy = self.view.displayGalaxy.isChecked()
        
    # def regenerateStarsHelper(self):
    #     Model.parameters.regenerateStars()
    #     Model.engine.reconfigure()

    def simImage(self):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        if self.enabled:
            self.playToggle = True
            parameters = self.parametersController.buildParameters()
            if parameters is None:
                return
            Model.updateParameters(parameters)
            controller = ControllerFactory(self.views)
            controller.run()
            self.thread = controller


    def record(self):
        """Calling this method will configure the system to save each frame of an animation, for compiling to a video that can be saved."""
        if self.enabled:
            self.recording = True
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
            if self.recording:
                self.fileManager.write()
            self.recording = False

    def qPoslabel_slot(self,pos):
        self.view.sourcePosLabel.setText(pos)