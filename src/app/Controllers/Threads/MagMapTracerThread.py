from PyQt5 import QtCore


from ...Views.Drawer.CompositeDrawerFactory import MagTracerComposite
from ...Utility.NullSignal import NullSignal
from ...Utility.Vec2D import Vector2D
from ...Models.Model import Model
import numpy as np
import time
import math



class MagMapTracerThread(QtCore.QThread):
    def __init__(self,signals=NullSignal,pixels = [],numFrames = -1):
        QtCore.QThread.__init__(self)
        self.signals = signals
        self.pixels = pixels.copy()
        if numFrames != -1:
            pixels = self._interpolate(pixels,numFrames)
            self.angles = pixels.copy()
#             self.angles[:,1] = pixels[:,0]
#             self.angles[:,0] = pixels[:,1]
        else:
            pixels = Model.parameters.extras.getParams('magmap').pixelToAngle(pixels)
            self.angles = pixels.copy()
#             self.angles[:,1] = pixels[:,0]
#             self.angles[:,0] = pixels[:,1]
        self.progress_bar_update  = signals['progressBar']
        self.progress_label_update = signals['progressLabel']
        self.image_canvas_update = signals['imageCanvas']
        self.curve_canvas_update = signals['curveCanvas']
        self.progress_bar_max_update = signals['progressBarMax']
        self.sourcePos_label_update = signals['paramLabel']
        self.tracer_signal_update = signals['tracerUpdate']
        self._updater = signals['tracerView']
        self.__calculating = False
        self.__frameRate = 60
#         self.__drawer = LensedImageLightCurveComposite(self.image_canvas_update,self.curve_canvas_update)
        self.__drawer = MagTracerComposite(NullSignal,NullSignal)
        self.circularPath = False
        self.__counter = 0

    def run(self):
        self.progress_label_update.emit("Ray-Tracing. Please Wait.")
        self.__calculating = True
        interval = 1/self.__frameRate
        self.progress_label_update.emit("Animating.")
        r = Model.parameters.quasar.radius.to('rad').value
        while self.__calculating and self.__counter < len(self.pixels):
            y = -self.angles[self.__counter,0]
            x = self.angles[self.__counter,1]
            pos = Vector2D(x,y,'rad')
            Model.parameters.quasar.setPos(pos)
#             pos = Model.parameters.extras.getParams('magmap').angleToPixel(pos)/1024
            timer = time.clock()
            pixels = Model.engine.getFrame()
            mag = Model.engine.getMagnification(pixels.shape[0])
            img,curve = self.__drawer.draw([Model.parameters,pixels],[mag])
            self._updater.emit(img,curve,self.pixels[self.__counter])
#             self.tracer_signal_update.emit(self.pixels[self.__counter])
            self.sourcePos_label_update.emit(str(Model.parameters.quasar.position.orthogonal.setUnit('rad').to('arcsec')))
            deltaT = time.clock() - timer
            if deltaT < interval:
                time.sleep(interval-deltaT)
            self.__counter += 1
        
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
        self.progress_label_update.emit("Paused.")
        self.__calculating = False

    def restart(self):
        self.progress_label_update.emit("Restarted.")
        self.__calculating = False
        pixels = Model.engine.getFrame(self.pixels[0,0],self.pixels[0,1],Model.parameters.quasar.radius.to('rad').value)
        mag = Model.engine.getMagnification(len(pixels))
        self.__drawer.draw([Model.parameters,pixels],[mag])
        self.tracer_signal_update.emit(self.pixels[0])
        self.sourcePos_label_update.emit(str(Model.parameters.quasar.position.orthogonal.setUnit('rad').to('arcsec')))
        self.__counter = 0
        self.__drawer.reset()

