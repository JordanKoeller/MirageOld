# from PyQt5 import QtCore

# import numpy as np

# from app.Models import ModelImpl
# from .FileManagers.MediaFileManager import MediaFileManager
# from .FileManagers.ParametersFileManager import ParametersFileManager
from .GUIController import GUIController
# from .Threads.MagMapTracerThread import MagMapTracerThread

# from ..Calculator.Engine.Engine_BruteForce import Engine_BruteForce
# from app.Utility.Vec2D import Vector2D


# class MagMapTracerController(GUIController):
#     '''
#     classdocs
#     '''
#     tracer_signal = QtCore.pyqtSignal(object)
#     update_view_signal = QtCore.pyqtSignal(object,object,object)
#     tracer_updated = QtCore.pyqtSignal(str)
#     run_done = QtCore.pyqtSignal(str)
#     save_lightCurve = QtCore.pyqtSignal()

#     def __init__(self, view,tracerView,trialName=None,trialNum=0):
#         '''
#         Constructor
#         '''
#         GUIController.__init__(self, view, None, None)
#         view.addSignals(tracerUpdate=self.tracer_signal,
#                         tracerView=self.update_view_signal,
#                         tracerUpdated=self.tracer_updated,
#                         tracerDone = self.run_done,
#                         saveLightCurve = self.save_lightCurve)
#         self.tracerView = tracerView
#         self.playToggle = False
#         self.thread = None
#         self.enabled = True
#         self.view.playPauseAction.triggered.connect(self.togglePlaying)
#         self.view.resetAction.triggered.connect(self.restart)
#         self.view.recordAction.triggered.connect(self.record)
#         self.view.actionLightCurve.triggered.connect(self.saveLightCurve)
#         self.view.showQuasarAction.triggered.connect(self.drawQuasarHelper)
#         self.view.showGalaxyAction.triggered.connect(self.drawGalaxyHelper)
#         self.view.signals['tracerUpdated'].connect(self.sendOffFrame)
#         self.view.signals['tracerDone'].connect(self.writeMov)
#         self.fileManager = MediaFileManager(self.view.signals)
#         self._showingQuasar = True
#         self._showingGalaxy = True
#         self.__initView()
#         self.initialize(trialName,trialNum)
#         self.animating = False

#     def __initView(self):
#         self.update_view_signal.connect(self.tracerView.updateAll)
#         self.tracerView.hasUpdated.connect(self.fileManager.sendFrame)
        
        
#     def togglePlaying(self):
#         if self.playToggle:
#             self.playToggle = False
#             self.pause()
#         else:
#             self.playToggle = True
#             self.simImage()
        

#     def show(self):
#         self.view.magTracerFrame.setHidden(False)
#         self.view.regenerateStars.setEnabled(False)
#         self.view.visualizationBox.setHidden(False)
#         self.enabled = True
        
#     def hide(self):
#         self.view.magTracerFrame.setHidden(True)
#         self.view.regenerateStars.setEnabled(True)
#         self.view.visualizationBox.setHidden(True)
#         self.enabled = False
        
#     def drawQuasarHelper(self):
#         """Interface for updating an animation in real time of whether or not to draw the physical location of the quasar to the screen as a guide."""
#         self._showingQuasar = not self._showingQuasar
#         ModelImpl.parameters.showQuasar = self._showingQuasar

#     def drawGalaxyHelper(self):
#         """
#         Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
#         """
#         self._showingGalaxy = not self._showingGalaxy
#         ModelImpl.parameters.showGalaxy = self._showingGalaxy
        

#     def simImage(self,recording=False):
#         """
#         Reads user input, updates the engine, and instructs the engine to begin
#         calculating what the user desired.

#         Called by default when the "Play" button is presssed.
#         """
#         if self.enabled:
# #             if recording:
# #                 self.tracerView.setUpdatesEnabled(False)
# #             else:
# #                 self.tracerView.setUpdatesEnabled(True)
#             if self.animating:
#                 self.tracerView.setUpdatesEnabled(recording)
#                 self.playToggle = True
#                 pixels = self.tracerView.getROI()
#                 self.thread = MagMapTracerThread(self.view.signals, pixels,recording=recording)
#                 self.thread.start()
#             else:
#                 pixels = self.tracerView.getROI()
#                 pixels = np.array(pixels,dtype=np.int)
#                 y = []
#                 for i in pixels:
#                     y.append(self.magmapRaw[i[0],i[1]])
#                 y = np.array(y)
#                 y = -2.5*np.log10(y)
#                 self.tracerView._updateLightCurve(np.arange(0,len(y)),y)
            
#     def saveLightCurve(self):
#         fname = 'filler'
#         resolution = 1000
#         track = self.tracerView.getROI()
#         track = ModelImpl.parameters.extras.getParams('magmap').pixelToAngle(track)
#         start = Vector2D(track[0][0],track[0][1],'rad')
#         finish = Vector2D(track[len(track)-1][0],track[len(track)-1][1],'rad')
#         yAxis = ModelImpl.engine.makeLightCurve(start,finish,resolution)
#         diff = (finish-start).magnitude()
#         xAxis = np.arange(0,diff,diff/resolution)
#         sE = np.array([[start.x,start.y],[finish.x,finish.y]])
#         np.savez(fname,xAxis = xAxis, yAxis = yAxis,startEnd = sE)
        

#     def record(self):
#         """Calling this method will configure the system to save each frame of an animation, for compiling to a video that can be saved."""
#         if self.enabled:
#             self.simImage(recording=True)

#     def pause(self):
#         if self.enabled:
#             self.playToggle = False
#             self.thread.pause()

#     def restart(self):
#         """Returns the system to its t=0 configuration. If the system was configured to record, will automatically prompt the user for a file name,
#         render and save the video."""
#         if self.enabled:
#             self.playToggle = False
#             self.thread.restart()
#             self.fileManager.cancelRecording()
            
#     def writeMov(self):
#         self.fileManager.write()
            
#     def sendOffFrame(self,filler):
#         frame = self.tracerView.getFrame()
#         self.fileManager.sendFrame(frame)
        
#     def initialize(self,fileName = None,trialNum=0):
#         from .. import lens_analysis
#         if fileName:
#             magmap,params = lens_analysis.load(fileName)[trialNum].traceQuasar()
#             self.magmapRaw = magmap.copy()
#             center = params.extras.getParams('magmap').center.to('rad')
#             engine = Engine_BruteForce()
#             engine.updateParameters(params)
#             baseMag = engine.query_raw_size(center.x,center.y,params.quasar.radius.to('rad').value)
#             baseMag = engine.getMagnification(baseMag)
#             baseMag = baseMag*255/magmap.max()
#             magmap = np.array(magmap*255/magmap.max(),dtype=np.uint8)
#             mag2 = magmap.copy()
#             mag2[:,0] = magmap.shape[0] - magmap[:,0]
#             mag2[:,1] = magmap[:,1]
#             self.tracerView.setMagMap(mag2,baseMag)
#             ModelImpl.updateParameters(params)
#         else:
#             paramsLoader = ParametersFileManager(self.view.signals)
#             params = paramsLoader.read()
#             magmap = self.fileManager.read()
#             if not params or not magmap:
#                 return False
#     #         self.view.bindFields(params)
#             array = np.asarray(magmap.convert('YCbCr'))[:,:,0]
#             self.tracerView.setMagMap(array)
#             ModelImpl.updateParameters(params)

    
#     def qPoslabel_slot(self, pos):
#         pass
# #         self.view.sourcePosLabel.setText(pos)
# # 

class MagMapTracerController(GUIController):


    def __init__(self,view):
        GUIController.__init__(self,view)


    def setMagmap(self,fileName = None, trialNum = 0):
        from .. import lens_analysis
        if fileName:
            magmap,params = lens_analysis.load(fileName)[trialNum].traceQuasar()
            self.magmapRaw = magmap.copy()
            center = params.extras.getParams('magmap').center.to('rad')
            engine = Engine_BruteForce()
            engine.updateParameters(params)
            baseMag = engine.query_raw_size(center.x,center.y,params.quasar.radius.to('rad').value)
            baseMag = engine.getMagnification(baseMag)
            baseMag = baseMag*255/magmap.max()
            magmap = np.array(magmap*255/magmap.max(),dtype=np.uint8)
            mag2 = magmap.copy()
            mag2[:,0] = magmap.shape[0] - magmap[:,0]
            mag2[:,1] = magmap[:,1]
            self.tracerView.setMagMap(mag2,baseMag)
            ModelImpl.updateParameters(params)
        else:
            paramsLoader = ParametersFileManager(self.view.signals)
            params = paramsLoader.read()
            magmap = self.fileManager.read()
            if not params or not magmap:
                return False
    #         self.view.bindFields(params)
            array = np.asarray(magmap.convert('YCbCr'))[:,:,0]
            self.tracerView.setMagMap(array)
            ModelImpl.updateParameters(params)

    
