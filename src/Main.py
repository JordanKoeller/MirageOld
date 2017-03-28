# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Engine_cl import Engine_cl as Engine
from Stellar import Galaxy
from Stellar import Quasar
import threading as par
from Utility import Vector2D, zeroVector
from enum import Enum
import time
from astropy import units as u
from Parameters import Parameters
from Main import ImageSimThread
from Main import LightCurveSimThread
from Graphics import DynamicCanvas

class GUIManager(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(GUIManager, self).__init__(parent)
        uic.loadUi('Resources/GUI/gui.ui', self)
        self.imgDrawer = ImageSimThread(self.main_canvas,progressBar = self.progressBar, progressLabel = self.progressLabel,engine = Engine())
        self.lightCurveDrawer = LightCurveSimThread(DynamicCanvas(self.canvasFrame), self.imgDrawer.engine, progressBar = self.progressBar, progressLabel = self.progressLabel)
        self.setupUi()


    def setupUi(self):
        """
        Adds functionality to the user interface. In other words, makes it so buttons, images, checkboxes, textfields, etc. do things.
        Override or add to method to alter user interraction outcomes.
        Called upon initialization.
        """
        self.pauseButton.clicked.connect(self.imgDrawer.pause)
        self.resetButton.clicked.connect(self.imgDrawer.restart)
        self.playButton.clicked.connect(self.simImage)
        self.displayQuasar.clicked.connect(self.drawQuasarHelper)
        self.displayGalaxy.clicked.connect(self.drawGalaxyHelper)
        self.progressBar.setValue(0)
        self.lightCurveStartButton.clicked.connect(self.calcLightCurve)
        self.saveStillButton.clicked.connect(self.saveStill)
        self.recordButton.clicked.connect(self.record)


    def __vector_from_qstring(self,string,reverse_y = True):
        """
        Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.
        Flips the sign of the y coordinate to translate computer coordinate systems of
        y increasing down to the conventional coordinate system of y increasing up.
        """
        x,y = (string.strip('()')).split(',')
        if (reverse_y):
            ret = Vector2D(float(x),-float(y))
            return ret
        else:
            ret = Vector2D(float(x),float(y))
            return ret

    def makeParameters(self):
        """
        Collects and parses all the information from the various user input fields/checkboxes.
        Stores them in instances of a Quasar class, Galaxy class, and Configs class.
        Returns the instances in that order as a tuple.
        """
        qVelocity = self.__vector_from_qstring(self.qVelocity.text()).setUnit('arcsec').to('rad')
        qPosition = self.__vector_from_qstring(self.qPosition.text()).setUnit('arcsec').to('rad')
        qRadius = u.Quantity(float(self.qRadius.text()),'arcsec')
        qRedshift = float(self.qRedshift.text())

        gRedshift = float(self.gRedshift.text())
        gVelDispersion = u.Quantity(float(self.gVelDispersion.text()),'km/s')
        gPercentStars = int(self.gNumStars.text())
        gShearMag = float(self.gShearMag.text())
        gShearAngle = u.Quantity(float(self.gShearAngle.text()),'degree')

        dTheta = u.Quantity(float(self.scaleInput.text()),'arcsec').to('rad').value
        canvasDim = int(self.dimensionInput.text())
        displayQuasar = self.displayQuasar.isChecked()
        displayGalaxy = self.displayGalaxy.isChecked()
        isMicrolensing = self.enableMicrolensingBox.isChecked()
        autoConfiguring = self.autoConfigCheckBox.isChecked()

        quasar = Quasar(qRedshift, qRadius, qPosition, qVelocity)
        galaxy = Galaxy(gRedshift, gVelDispersion, gShearMag, gShearAngle, gPercentStars)
        params = Parameters(isMicrolensing, autoConfiguring, galaxy, quasar, dTheta, canvasDim, displayGalaxy, displayQuasar)
        return params


    def drawQuasarHelper(self):
        self.imgDrawer.engine.parameters.showQuasar = self.displayQuasar.isChecked()

    def drawGalaxyHelper(self):
        self.imgDrawer.engine.parameters.showGalaxy = self.displayGalaxy.isChecked()

    def calcLightCurve(self):
        start = self.__vector_from_qstring(self.lightCurveMinField.text()).setUnit('arcsec').to('rad')
        end = self.__vector_from_qstring(self.lightCurveMaxField.text()).setUnit('arcsec').to('rad')
        self.lightCurveDrawer.canvas.setParent(self.canvasFrame)
        self.imgDrawer.canvas.hide()
        self.lightCurveDrawer.canvas.show()
        self.lightCurveDrawer.setLightCurveLimits(start,end)
        self.lightCurveDrawer.updateParameters(self.makeParameters())
        self.lightCurveDrawer.start()
    def simImage(self):
        """
        Reads user input, updates the engine, and instructs the engine to begin
        __calculating what the user desired.

        Called by default when the "Play" button is presssed.
        """
        # self.main_canvas = self.imgDrawer.canvas
        # self.imgDrawer.canvas.setParent(self.canvasFrame)
        self.lightCurveDrawer.canvas.hide()
        self.imgDrawer.canvas.show()
        parameters = self.makeParameters()
        self.imgDrawer.updateParameters(parameters)
        self.imgDrawer.start()

    def saveStill(self):
        self.imgDrawer.canvas.pixmap().save("../SavedFiles/"+self.fileNameField.text()+".png")

    def record(self):
        self.imgDrawer.toggleRecording("../SavedFiles/"+self.fileNameField.text()+".mp4")
        self.simImage()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = GUIManager()
    ui.show()
    sys.exit(app.exec_())
