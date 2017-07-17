'''
Created on May 31, 2017

@author: jkoeller
'''

from PyQt5 import QtCore, QtGui

from .GUIController import GUIController
from .Threads.VisualizerThread import VisualizerThread
from .FileManagers.FITSFileManager import FITSFileManager
from .FileManagers.VisualizationFileManager import VisualizationFileManager
from ..Models.Model import Model


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
        self.view.pauseButton.clicked.connect(self.pause)
        self.view.resetButton.clicked.connect(self.restart)
        self.view.playButton.clicked.connect(self.simImage)
        self.view.playPauseAction.triggered.connect(self.togglePlaying)
        self.view.resetAction.triggered.connect(self.restart)
        self.view.displayQuasar.clicked.connect(self.drawQuasarHelper)
        self.view.displayGalaxy.clicked.connect(self.drawGalaxyHelper)
        self.view.record_button.triggered.connect(self.record)
        self.view.visualizeDataButton.clicked.connect(self.visualizeData)
        self.view.developerExportButton.clicked.connect(self.saveVisualization)
        self.view.regenerateStars.clicked.connect(self.regenerateStarsHelper)
        filler_img = QtGui.QImage(2000, 2000, QtGui.QImage.Format_Indexed8)
        filler_img.setColorTable([QtGui.qRgb(0, 0, 0)])
        filler_img.fill(0)
        self.view.main_canvas.setPixmap(QtGui.QPixmap.fromImage(filler_img))
        self.view.signals["imageCanvas"].connect(self.main_canvas_slot)
        self.view.signals["curveCanvas"].connect(self.curve_canvas_slot)
        self.view.signals['paramLabel'].connect(self.qPoslabel_slot)
        self.parametersController = self.view.parametersController
        self.fileManager = VisualizationFileManager(self.view.signals)

    def togglePlaying(self):
        if self.playToggle:
            self.playToggle = False
            self.pause()
        else:
            self.playToggle = True
            self.simImage()
        

    def show(self):
        self.view.visualizationFrame.setHidden(False)
        self.view.visualizationBox.setHidden(False)
        self.enabled = True
        
    def hide(self):
        self.view.visualizationBox.setHidden(True)
        self.view.visualizationFrame.setHidden(True)
        self.enabled = False
        
    def drawQuasarHelper(self):
        """Interface for updating an animation in real time of whether or not to draw the physical location of the quasar to the screen as a guide."""
        Model.parameters.showQuasar = self.view.displayQuasar.isChecked()

    def drawGalaxyHelper(self):
        """
        Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
        """
        Model.parameters.showGalaxy = self.view.displayGalaxy.isChecked()
        
    def regenerateStarsHelper(self):
        Model.parameters.regenerateStars()
        Model.engine.reconfigure()

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
        
        
    def visualizeData(self):
        params = self.parametersController.buildParameters()
        return self.thread.visualize(params)

    def saveVisualization(self):
        """Calculates and saves a point-source magnification map as a FITS file"""
        fitsFileManager = FITSFileManager(self.view.signals)
        data = self.visualizeData()
        fitsFileManager.write(data)
        # self.fileManager.save_still(self.main_canvas)

        
    def main_canvas_slot(self, img):
        img = QtGui.QImage(img.T.tobytes(),img.shape[0],img.shape[1],QtGui.QImage.Format_Indexed8)
        img.setColorTable(Model.colorMap)
        self.view.main_canvas.pixmap().convertFromImage(img)
        self.view.main_canvas.update()
        self.fileManager.giveFrame(img)

    def curve_canvas_slot(self, x, y):
        self.view.curve_canvas.plot(x, y, clear=True)
    
    def qPoslabel_slot(self,pos):
        self.view.sourcePosLabel.setText(pos)
        
# 
