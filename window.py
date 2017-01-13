# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Engine_cl import Engine_cl
from Configs import Configs
from stellar import Galaxy
from stellar import Quasar
from stellar import defaultGalaxy
from stellar import defaultQuasar
from Configs import defaultConfigs
from stellar import microGalaxy
from stellar import microQuasar
from Configs import microConfigs
import threading as par
from Vector2D import Vector2D
from enum import Enum
import time
from astropy import units as u

class CanvasType(Enum):
    LABEL_CANVAS = 0
    MPL_CANVAS = 1
    NONE_TYPE = 2

class SimThread(QtCore.QThread):
    def __init__(self,engine,canvas = None):
        QtCore.QThread.__init__(self)
        self.engine = engine
        self.canvas = canvas
        self.calculating = False
        self.reconfiguring = False


    def setCanvas(self,canvas, canvasType = CanvasType.LABEL_CANVAS):
        self.canvas = canvas
        filler_img = QtGui.QImage(800,800, QtGui.QImage.Format_Indexed8)
        filler_img.setColorTable([QtGui.qRgb(0,0,0)])
        filler_img.fill(0)
        self.canvas.setPixmap(QtGui.QPixmap.fromImage(filler_img))

    def run(self):
        self.canvas.setPixmap(QtGui.QPixmap.fromImage(self.engine.img))
        self.calculating = True
        interval = 1/self.engine.configs.frameRate
        while self.calculating:
            timer = time.clock()
            frame = self.engine.drawFrame()
            self.engine.time += self.engine.configs.dt
            self.canvas.pixmap().convertFromImage(frame)
            self.canvas.update()
            deltaT = time.clock() - timer
            if deltaT < interval:
                time.sleep(interval-deltaT)

    def pause(self):
        self.calculating = False

    def restart(self):
        self.pause()
        self.engine.time = 0.0
        frame = self.engine.drawFrame()
        self.canvas.pixmap().convertFromImage(frame)
        self.canvas.update()




class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(Ui_MainWindow, self).__init__(parent)
        uic.loadUi('GUI.ui', self)
        self.simThread = SimThread(Engine_cl(defaultQuasar,defaultGalaxy,defaultConfigs, auto_configure = False))
        self.setupUi()

    def setupUi(self):
        """
        Adds functionality to the user interface. In other words, makes it so buttons, images, checkboxes, textfields, etc. do things.
        Override or add to method to alter user interraction outcomes.
        Called upon initialization.
        """
        self.simThread.setCanvas(self.main_canvas)
        self.pauseButton.clicked.connect(self.simThread.pause)
        self.resetButton.clicked.connect(self.simThread.restart)
        self.playButton.clicked.connect(self.startSim)


    def __vector_from_qstring(self,string):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.
        Flips the sign of the y coordinate to translate computer coordinate systems of
        y increasing down to the conventional coordinate system of y increasing up.
        """
        x,y = (string.strip('()')).split(',')
        ret = Vector2D(float(x),-float(y))
        return ret

    def pull_from_input(self):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        Stores them in instances of a Quasar class, Galaxy class, and Configs class.
        Returns the instances in that order as a tuple.
        """
        qVelocity = self.__vector_from_qstring(self.qVelocity.text()).setUnit('arcsec')
        qPosition = self.__vector_from_qstring(self.qPosition.text()).setUnit('arcsec')
        qRadius = u.Quantity(float(self.qRadius.text()),'arcsec')
        qRedshift = float(self.qRedshift.text())
        gRedshift = float(self.gRedshift.text())
        gVelDispersion = u.Quantity(float(self.gVelDispersion.text()),'km/s')
        gNumStars = int(self.gNumStars.text())
        gShearMag = float(self.gShearMag.text())
        gShearAngle = u.Quantity(float(self.gShearAngle.text()),'degree')
        quasar = Quasar(qRedshift,qPosition,qRadius,qVelocity)
        galaxy = Galaxy(gRedshift,gVelDispersion,gShearMag,gShearAngle,u.Quantity(0.00,'rad'),gNumStars)
        colorLenseImg = self.colorLenseImg.isChecked()
        displayQuasar = self.displayQuasar.isChecked()
        displayGalaxy = self.displayGalaxy.isChecked()
        configs = Configs(1/25,.001/625, Vector2D(800,800), 25, displayGalaxy, displayQuasar)
        return (quasar,galaxy,configs)

    def startSim(self):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        quasar,galaxy,configs = self.pull_from_input()
        self.simThread.engine.updateQuasar(quasar,auto_configure = False)
        self.simThread.engine.updateGalaxy(galaxy,auto_configure = False)
        auto_generate_configs = True
        self.simThread.engine.updateConfigs(configs = configs,auto_configure = False)
        if auto_generate_configs:
            self.simThread.engine.updateConfigs(dTheta = 1.5*1.3*self.simThread.engine.einsteinRadius/400)
        self.simThread.start()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())

