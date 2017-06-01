'''
Created on May 31, 2017

@author: jkoeller
'''
import time

from PyQt5 import QtCore

from Controllers.GUIController import GUIController
import Models
from Views.Drawer import DataVisualizerDrawer
from Views.Drawer.CompositeDrawerFactory import LensedImageLightCurveComposite


class VisualizationController(GUIController, QtCore.QThread):
    '''
    classdocs
    '''
    image_canvas_update = QtCore.pyqtSignal(object)
    curve_canvas_update = QtCore.pyqtSignal(object, object)

    def __init__(self, view):
        '''
        Constructor
        '''
        GUIController.__init__(self)
        QtCore.QThread.__init__(self)
        self.progress_bar_update = view.signals[0]
        self.progress_label_update = view.signals[1]
        self.image_canvas_update = view.signals[2]
        self.curve_canvas_update = view.signals[3]
        self.progress_bar_max_update = view.signals[4]
        self.sourcePos_label_update = view.signals[5]
        self.__calculating = False
        self.__frameRate = 60
        self.__drawer = LensedImageLightCurveComposite(self.image_canvas_update, self.curve_canvas_update)
        self.parameters = None
        self.circularPath = False
        
    @property
    def signals(self):
        return {"image_canvas_update":self.image_canvas_update, "curve_canvas_update":self.curve_canvas_update}
        
    @property
    def slots(self):
        return {"image_canvas_slot":self.main_canvas_slot, "curve_canvas_slot":self.curve_canvas_slot}

    def drawGalaxyHelper(self):
        """
        Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
        """
        self.simThread.engine.parameters.showGalaxy = self.displayGalaxy.isChecked()

    def simImage(self):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        parameters = self.makeParameters()
        if parameters is None:
            return
        self.simThread.updateParameters(parameters)
        self.simThread.start()

    def record(self):
        """Calling this method will configure the system to save each frame of an animation, for compiling to a video that can be saved."""
        self.fileManager.recording = True
        self.simImage()

    def restart(self):
        """Returns the system to its t=0 configuration. If the system was configured to record, will automatically prompt the user for a file name,
        render and save the video."""
        self.progress_label_update.emit("Restarted.")
        self.__calculating = False
        self.parameters.setTime(0)
        pixels = Models.engine.getFrame()
        mag = Models.engine.getMagnification(len(pixels))
        frame = self.__drawer.draw([self.parameters, pixels], [mag])
        self.sourcePos_label_update.emit(str(self.parameters.quasar.position.orthogonal.setUnit('rad').to('arcsec')))
        self.__drawer.reset()
        self.fileManager.save_recording()
        
        
    def visualizeData(self):
        params = self.makeParameters()
        return self.simThread.visualize(params)

    def saveVisualization(self):
        """Calculates and saves a point-source magnification map as a FITS file"""
        self.fileManager.recording = True
        data = self.visualizeData()
        self.fileManager.save_fitsFile(data)
        
    def main_canvas_slot(self, img):
        self.main_canvas.pixmap().convertFromImage(img)
        self.main_canvas.update()
        self.fileManager.giveFrame(img)

    def curve_canvas_slot(self, x, y):
        self.curve_canvas.plot(x, y, clear=True)
        
    def updateParameters(self, params):
        if self.parameters:
            params.setTime(self .parameters.time)
            params.quasar.setPos(self.parameters.quasar.observedPosition)
        self.parameters = params

    def run(self):
        self.progress_label_update.emit("Ray-Tracing. Please Wait.")
        Models.engine.updateParameters(self.parameters)
        self.__calculating = True
        interval = 1 / self.__frameRate
        counter = 0
        self.progress_label_update.emit("Animating.")
        while self.__calculating:
            counter += 1
            timer = time.clock()
            pixels = Models.engine.getFrame()
            mag = Models.engine.getMagnification(len(pixels))
            img = self.__drawer.draw([self.parameters, pixels], [mag])
            self.sourcePos_label_update.emit(str(self.parameters.quasar.position.orthogonal.setUnit('rad').to('arcsec')))
            # if self.circularPath:
            self.parameters.quasar.circularPath()
            self.parameters.incrementTime(self.parameters.dt)
            deltaT = time.clock() - timer
            if deltaT < interval:
                time.sleep(interval - deltaT)


    def pause(self):
        self.progress_label_update.emit("Paused.")
        self.__calculating = False

    def visualize(self, params):
        self.progress_label_update.emit("Ray-Tracing. Please Wait.")
        drawer = DataVisualizerDrawer(self.image_canvas_update)
        Models.engine.updateParameters(params)
        self.progress_label_update.emit("Calculating Magnification Coefficients. Please Wait.")
        pixels = Models.engine.visualize()
        frame = drawer.draw([pixels])
        self.progress_label_update.emit("Done.")
        return pixels
