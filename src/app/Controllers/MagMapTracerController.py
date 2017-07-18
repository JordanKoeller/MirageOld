from PyQt5 import QtCore

import numpy as np

from ..Models.Model import Model
from .FileManagers.MediaFileManager import MediaFileManager
from .FileManagers.ParametersFileManager import ParametersFileManager
from .GUIController import GUIController
from .Threads.MagMapTracerThread import MagMapTracerThread
from .. import lens_analysis
from ..Calculator.Engine.Engine_BruteForce import Engine_BruteForce


class MagMapTracerController(GUIController):
    '''
    classdocs
    '''
    tracer_signal = QtCore.pyqtSignal(object)
    update_view_signal = QtCore.pyqtSignal(object,object,object)
    tracer_updated = QtCore.pyqtSignal(str)
    run_done = QtCore.pyqtSignal(str)

    def __init__(self, view,tracerView,trialName=None,trialNum=0):
        '''
        Constructor
        '''
        GUIController.__init__(self, view, None, None)
        view.addSignals(tracerUpdate=self.tracer_signal,tracerView=self.update_view_signal,tracerUpdated=self.tracer_updated,tracerDone = self.run_done)
        self.tracerView = tracerView
        self.playToggle = False
        self.thread = None
        self.enabled = True
        self.view.playPauseAction.triggered.connect(self.togglePlaying)
        self.view.resetAction.triggered.connect(self.restart)
        self.view.recordAction.triggered.connect(self.record)
        self.view.showQuasarAction.triggered.connect(self.drawQuasarHelper)
        self.view.showGalaxyAction.triggered.connect(self.drawGalaxyHelper)
        self.view.signals['tracerUpdated'].connect(self.sendOffFrame)
        self.view.signals['tracerDone'].connect(self.writeMov)
        self.fileManager = MediaFileManager(self.view.signals)
        self._showingQuasar = True
        self._showingGalaxy = True
        self.__initView()
        self.initialize(trialName,trialNum)
            

    def __initView(self):
        self.update_view_signal.connect(self.tracerView.updateAll)
        self.tracerView.hasUpdated.connect(self.fileManager.sendFrame)
        
        
    def togglePlaying(self):
        if self.playToggle:
            self.playToggle = False
            self.pause()
        else:
            self.playToggle = True
            self.simImage()
        

    def show(self):
        self.view.magTracerFrame.setHidden(False)
        self.view.regenerateStars.setEnabled(False)
        self.view.visualizationBox.setHidden(False)
        self.enabled = True
        
    def hide(self):
        self.view.magTracerFrame.setHidden(True)
        self.view.regenerateStars.setEnabled(True)
        self.view.visualizationBox.setHidden(True)
        self.enabled = False
        
    def drawQuasarHelper(self):
        """Interface for updating an animation in real time of whether or not to draw the physical location of the quasar to the screen as a guide."""
        self._showingQuasar = not self._showingQuasar
        Model.parameters.showQuasar = self._showingQuasar

    def drawGalaxyHelper(self):
        """
        Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
        """
        self._showingGalaxy = not self._showingGalaxy
        Model.parameters.showGalaxy = self._showingGalaxy
        

    def simImage(self,recording=False):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        if self.enabled:
#             if recording:
#                 self.tracerView.setUpdatesEnabled(False)
#             else:
#                 self.tracerView.setUpdatesEnabled(True)
            self.tracerView.setUpdatesEnabled(recording)
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
        self.fileManager.write()
            
    def sendOffFrame(self,filler):
        frame = self.tracerView.getFrame()
        self.fileManager.sendFrame(frame)
        
    def initialize(self,fileName = None,trialNum=0):
        if fileName:
            magmap,params = lens_analysis.load(fileName)[trialNum].traceQuasar()
            magmap2 = np.ones_like(magmap)
            for i in range(magmap.shape[0]):
                for j in range(magmap.shape[1]):
                    magmap2[magmap.shape[0]- 1 -i,magmap.shape[1] - 1 -j] = magmap[i,j]
            center = params.extras.getParams('magmap').center.to('rad')
            engine = Engine_BruteForce()
            engine.updateParameters(params)
            baseMag = engine.query_raw_size(center.x,center.y,params.quasar.radius.to('rad').value)
            baseMag = engine.getMagnification(baseMag)
            baseMag = baseMag*255/magmap2.max()
#             print("BaseMag = " +str(baseMag))
            magmap = np.array(magmap2*255/magmap2.max(),dtype=np.uint8)
            self.tracerView.setMagMap(magmap,baseMag)
            Model.updateParameters(params)
        else:
            paramsLoader = ParametersFileManager(self.view.signals)
            params = paramsLoader.read()
            magmap = self.fileManager.read()
            if not params or not magmap:
                return False
    #         self.view.bindFields(params)
            array = np.asarray(magmap.convert('YCbCr'))[:,:,0]
            self.tracerView.setMagMap(array)
            Model.updateParameters(params)

    
    def qPoslabel_slot(self, pos):
        pass
#         self.view.sourcePosLabel.setText(pos)
# 
