# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from Stellar import Galaxy
from Stellar import Quasar
import threading as par
from Utility import Vector2D, zeroVector
import time
from astropy import units as u
from Parameters import Parameters
from Main import SimThread
from Graphics import DynamicCanvas
import pyqtgraph as pg
from Main import FileManager
from Engine_Grid import Engine_Grid
from Engine_KDTree import Engine_KDTree
import sys


class GUIManager(QtWidgets.QMainWindow):
	progress_bar_update = QtCore.pyqtSignal(int)
	progress_label_update = QtCore.pyqtSignal(str)
	sourcePos_label_update = QtCore.pyqtSignal(str)
	image_canvas_update = QtCore.pyqtSignal(object)
	curve_canvas_update = QtCore.pyqtSignal(object, object)
	progress_bar_max_update = QtCore.pyqtSignal(int)

	def __init__(self, parent=None):
		super(GUIManager, self).__init__(parent)
		uic.loadUi('Resources/GUI/gui.ui', self)
		signals = self.makeSignals()
		self.simThread = SimThread(Engine_Grid(), signals)
		self.fileManager = FileManager(signals)
		self.setupUi()
		self.setupSignals()

	def setupSignals(self):

		"""
		Internally called method for connecting Qt signals and slots for efficient UI control.
		"""
		self.image_canvas_update.connect(self.main_canvas_slot)
		self.curve_canvas_update.connect(self.curve_canvas_slot)
		self.progress_bar_update.connect(self.progress_bar_slot)
		self.progress_bar_max_update.connect(self.progress_bar_max_slot)
		self.progress_label_update.connect(self.progress_label_slot)
		self.sourcePos_label_update.connect(self.sourcePos_label_slot)

	def makeSignals(self):
		"""
		Provides a list of all the created slots for UI updates and feedback.
		"""
		return [self.progress_bar_update, self.progress_label_update, self.image_canvas_update,
				self.curve_canvas_update, self.progress_bar_max_update, self.sourcePos_label_update]

	def setupUi(self):
		"""
		Adds functionality to the user interface. In other words, makes it so buttons, images, checkboxes, textfields, etc. do things.
		Override or add to method to alter user interraction outcomes.
		Called upon initialization.
		"""
		self.playButton.clicked.connect(self.simImage)
		self.displayQuasar.clicked.connect(self.drawQuasarHelper)
		self.displayGalaxy.clicked.connect(self.drawGalaxyHelper)
		self.progressBar.setValue(0)
		# self.lightCurveStartButton.clicked.connect(self.calcLightCurve)
		self.pauseButton.clicked.connect(self.simThread.pause)
		self.resetButton.clicked.connect(self.restart)
		self.load_setup.triggered.connect(self.loadParams)
		self.save_setup.triggered.connect(self.saveParams)
		self.shutdown.triggered.connect(sys.exit)
		self.record_button.triggered.connect(self.record)
		self.visualizeDataButton.clicked.connect(self.visualizeData)
		self.developerExportButton.clicked.connect(self.saveVisualization)
		# self.binSizeTestButton.clicked.connect(self.simThread.bin_test)
		filler_img = QtGui.QImage(2000, 2000, QtGui.QImage.Format_Indexed8)
		filler_img.setColorTable([QtGui.qRgb(0, 0, 0)])
		filler_img.fill(0)
		self.main_canvas.setPixmap(QtGui.QPixmap.fromImage(filler_img))

	def __vector_from_qstring(self, string, reverse_y=False, transpose=True):
		"""
		Converts an ordered pair string of the form (x,y) into a Vector2D of x and y.

		Parameters:
			reverse_y : Boolean
				specify whether or not to negate y-coordinates to convert a conventional coordinate system of positive y in the up direction to
				positive y in the down direction as used by graphics libraries. Default False

			transpose : Boolean
				Specify whether or not to flip x and y coordinates. In other words, return a Vector2D of (y,x) rather than (x,y). Default True
		"""
		x, y = (string.strip('()')).split(',')

		if transpose:
			if reverse_y:
				return Vector2D(-float(y), float(x))
			else:
				return Vector2D(float(y), float(x))
		else:
			if reverse_y:
				return Vector2D(float(x), -float(y))
			else:
				return Vector2D(float(x), float(y))

	def makeParameters(self):
		"""
		Collects and parses all the information from the various user input fields/checkboxes.
		Stores them in a Parameters object.
		If the user inputs invalid arguments, will handle the error by returning None and sending a message
		to the progress_label_slot saying "Error. Input could not be parsed to numbers."
		"""
		try:
			qVelocity = self.__vector_from_qstring(self.qVelocity.text()).setUnit('arcsec').to('rad')
			qPosition = self.__vector_from_qstring(self.qPosition.text()).setUnit('arcsec').to('rad')
			qRadius = u.Quantity(float(self.qRadius.text()), 'arcsec')
			qRedshift = float(self.qRedshift.text())

			gRedshift = float(self.gRedshift.text())
			gVelDispersion = u.Quantity(float(self.gVelDispersion.text()), 'km/s')
			gNumStars = int(self.gNumStars.text())
			gShearMag = float(self.gShearMag.text())
			gShearAngle = u.Quantity(float(self.gShearAngle.text()), 'degree')

			displayCenter = self.__vector_from_qstring(self.gCenter.text()).setUnit('arcsec').to('rad')
			dTheta = u.Quantity(float(self.scaleInput.text()), 'arcsec').to('rad')
			canvasDim = int(self.dimensionInput.text())
			displayQuasar = self.displayQuasar.isChecked()
			displayGalaxy = self.displayGalaxy.isChecked()

			quasar = Quasar(qRedshift, qRadius, qPosition, qVelocity)
			galaxy = Galaxy(gRedshift, gVelDispersion, gShearMag, gShearAngle, gNumStars, center=displayCenter)
			params = Parameters(galaxy, quasar, dTheta, canvasDim, displayGalaxy, displayQuasar)
			# params.circularPath = self.circularPathBox.isChecked()
			return params
		except ValueError:
			self.progress_label_slot("Error. Input could not be parsed to numbers.")
			return None

	def drawQuasarHelper(self):
		"""Interface for updating an animation in real time of whether or not to draw the physical location of the quasar to the screen as a guide."""
		self.simThread.engine.parameters.showQuasar = self.displayQuasar.isChecked()

	def drawGalaxyHelper(self):
		"""
		Interface for updating an animation in real time of whether or not to draw the lensing galaxy's center of mass, along with any stars".
		"""
		self.simThread.engine.parameters.showGalaxy = self.displayGalaxy.isChecked()

	def calcLightCurve(self):
		"""
		Deprecated
		"""
		start = self.__vector_from_qstring(self.lightCurveMinField.text()).setUnit('arcsec').to('rad')
		end = self.__vector_from_qstring(self.lightCurveMaxField.text()).setUnit('arcsec').to('rad')

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
		self.simThread.restart()
		self.fileManager.save_recording()

	def saveParams(self):
		"""Prompts the user for a file name, then saves the lensing system's parameters to be loaded in at a later session."""
		print("Firing")
		self.fileManager.writeParams(self.makeParameters())

	def loadParams(self):
		"""Prompts the user to select a previously savd lensing system configuration, then when selected loads the system to model"""
		params = self.fileManager.readParams()
		self.bindFields(params)

	def visualizeData(self):
		params = self.makeParameters()
		return self.simThread.visualize(params)

	def saveVisualization(self):
		"""Calculates and saves a point-source magnification map as a FITS file"""
		self.fileManager.recording = True
		data = self.visualizeData()
		self.fileManager.save_fitsFile(data)
		# self.fileManager.save_still(self.main_canvas)

	def bindFields(self, parameters):
		"""Sets the User interface's various input fields with the data in the passed-in parameters object."""
		qV = parameters.quasar.velocity.to('arcsec').unitless()
		qP = parameters.quasar.position.to('arcsec').unitless()
		gP = parameters.galaxy.position.to('arcsec').unitless()
		self.qVelocity.setText("(" + str(qV.y) + "," + str(qV.x) + ")")
		self.qPosition.setText("(" + str(qP.y) + "," + str(qP.x) + ")")
		self.gCenter.setText("(" + str(gP.y) + "," + str(gP.x) + ")")
		self.qRadius.setText(str(parameters.quasar.radius.to('arcsec').value))
		self.qRedshift.setText(str(parameters.quasar.redshift))

		self.gRedshift.setText(str(parameters.galaxy.redshift))
		self.gVelDispersion.setText(str(parameters.galaxy.velocityDispersion.value))
		self.gNumStars.setText(str(parameters.galaxy.numStars))
		self.gShearMag.setText(str(parameters.galaxy.shearMag))
		self.gShearAngle.setText(str(parameters.galaxy.shearAngle.to('degree').value))

		self.scaleInput.setText(str(parameters.dTheta.to('arcsec').value * parameters.canvasDim))
		self.dimensionInput.setText(str(parameters.canvasDim))
		self.displayQuasar.setChecked(parameters.showQuasar)
		self.displayGalaxy.setChecked(parameters.showGalaxy)

	# SIGNAL METHODS
	def main_canvas_slot(self, img):
		self.main_canvas.pixmap().convertFromImage(img)
		self.main_canvas.update()
		self.fileManager.giveFrame(img)

	def curve_canvas_slot(self, x, y):
		self.curve_canvas.plot(x, y, clear=True)

	def progress_bar_slot(self, value):
		self.progressBar.setValue(value)

	def progress_bar_max_slot(self, n):
		self.progressBar.setMaximum(n)

	def progress_label_slot(self, text):
		self.progressLabel.setText(text)

	def sourcePos_label_slot(self, text):
		self.sourcePosLabel.setText(text)


if __name__ == "__main__":
	import os

	print("Process ID = " + str(os.getpid()))
	app = QtWidgets.QApplication(sys.argv)
	ui = GUIManager()
	ui.show()
	sys.exit(app.exec_())
