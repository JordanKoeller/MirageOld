from PyQt5 import QtCore


from ...Views.Drawer.CompositeDrawerFactory import MagTracerComposite
from ...Utility.NullSignal import NullSignal
from ...Utility.Vec2D import Vector2D
from ...Models.Model import Model
import numpy as np
import time



class MagMapTracerThread(QtCore.QThread):
    def __init__(self,signals=NullSignal,pixels = [],numFrames = -1,recording=False):
        QtCore.QThread.__init__(self)
        self.signals = signals
        self.pixels = pixels.copy()
        if numFrames != -1:
            pixels = self._interpolate(pixels,numFrames)
            self.angles = pixels.copy()
        else:
            pixels = Model.parameters.extras.getParams('magmap').pixelToAngle(pixels)
            self.angles = pixels.copy()
        self.__calculating = False
        self.__frameRate = 25
        self.__drawer = MagTracerComposite(NullSignal,NullSignal)
        self.circularPath = False
        self.__counter = 0
        self.recording=recording

    def run(self):
        self.signals['progressLabel'].emit("Ray-Tracing. Please Wait.")
        self.__calculating = True
        interval = 1/self.__frameRate
        if self.recording:
            self.signals['progressDialog'].emit(0,len(self.pixels)-1,'Tracing Quasar. Please Wait.')
        self.signals['progressLabel'].emit("Tracing.")
#         self.signals['progressDialog'].emit(0,len(self.angles),'Tracing Quasar. Please Wait.')
        while self.__calculating and self.__counter < len(self.pixels):
#             self.progress_bar_update.emit(self.__counter)
            x = self.angles[self.__counter,0]
            y = self.angles[self.__counter,1]
            pos = Vector2D(x,y,'rad')
            Model.parameters.quasar.setPos(pos)
            timer = time.clock()
            if self.recording:
                self.signals['tracerUpdated'].emit('Done')
            pixels = Model.engine.getFrame()
            mag = Model.engine.getMagnification(pixels.shape[0])
            img,curve = self.__drawer.draw([Model.parameters,pixels],[mag])
            self.signals['tracerView'].emit(img,curve,self.pixels[self.__counter])
            self.signals['progressBar'].emit(self.__counter)
            if not self.recording:
                deltaT = time.clock() - timer
                if deltaT < interval:
                    time.sleep(interval-deltaT)
            self.__counter += 1
        self.signals['progressLabel'].emit("Done")
        if self.recording:
            self.signals['tracerDone'].emit('Finished')
        
    def _interpolate(self,pixels,numFrames):
        start = pixels[0]
        end = pixels[len(pixels)-1]
        dx = (end[0]-start[0])/numFrames
        dy = (end[0]-start[0])/numFrames
        pixels = np.ndarray((numFrames,2))
        for i in range(numFrames):
            pixels[i] = [start[0]+i*dx,start[1]+dy*i]
        return Model.parameters.extras.getParams('magmap').pixelToAngle(pixels)

        
    def pause(self):
        self.signals['progressLabel'].emit("Paused.")
        self.__calculating = False

    def restart(self):
        self.signals['progressLabel'].emit("Restarted.")
        self.__calculating = False
        pixels = Model.engine.getFrame(self.pixels[0,0],self.pixels[0,1],Model.parameters.quasar.radius.to('rad').value)
        mag = Model.engine.getMagnification(len(pixels))
        self.__drawer.draw([Model.parameters,pixels],[mag])
        self.signals['tracerUpdate'].emit(self.pixels[0])
#         self.sourcePos_label_update.emit(str(Model.parameters.quasar.position.to('arcsec')))
        self.__counter = 0
        self.__drawer.reset()

