import sys

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QProgressDialog
from PyQt5 import QtCore, QtWidgets

import factory

from .. import mainUIFile
from ..Utility import Vector2D
from ..Utility.SignalRepo import SignalRepo
from ..Controllers import ControllerFactory
from .LensedImageView import LensedImageView
from .LightCurvePlotView import LightCurvePlotView
from .ViewLayout import ViewLayout
import factory
from ..Models.Model import Model

class MainView(QtWidgets.QMainWindow,SignalRepo):
	"""

	"""

	playSignal = QtCore.pyqtSignal()
	pauseSignal = QtCore.pyqtSignal()
	resetSignal = QtCore.pyqtSignal()
	progressDialogSignal = QtCore.pyqtSignal(int,int,str)
	progressLabelSignal = QtCore.pyqtSignal(str)

	def __init__(self, parent=None):
		super(MainView, self).__init__()
		uic.loadUi(mainUIFile,self)
		self.addSignals(progressLabel = self.progressLabelSignal,
						play = self.playSignal,
						pause = self.pauseSignal,
						reset = self.resetSignal,
						progressDialog = self.progressDialogSignal
						)
		self.actionAddImgPane.triggered.connect(self.addImgPane)
		self.actionAddMagPane.triggered.connect(self.addMagPane)
		self.actionAddCurvePane.triggered.connect(self.addCurvePane)
		self.actionAddModel.triggered.connect(self.addModel)
		self.parent = parent
		self.progressDialogSignal.connect(self.openDialog)
		self.controller = None
		self.views = []
		self.isPlaying = False
		self.parametersController = factory._ParametersControllerFactory(self)
		self.layout = ViewLayout(None,None)
		self.mainSplitter.addWidget(self.layout)
		self.initVisCanvas()
		self._mkStatusBar()

	def _playPauseToggle(self):
		if self.isPlaying:
			self.isPlaying = False
			self.pauseSignal.emit()
			del(self.controller)
		else:
			paramters = self.parametersController.buildParameters()
			if paramters:
				Model.updateParameters(paramters)
				self.controller = ControllerFactory(self.views,self.playSignal,self.pauseSignal,self.resetSignal)
				self.isPlaying = True
				self.playSignal.emit()

	def _resetHelper(self):
		self.isPlaying = False
		self.resetSignal.emit()

	def initVisCanvas(self):
		self.addCurvePane()
		self.addImgPane()

	def addImgPane(self):
		imgCanvas = LensedImageView(None)
		self.layout.addView(imgCanvas)
		self.views.append(imgCanvas)

	def addCurvePane(self):
		plCanvas = LightCurvePlotView(None)
		self.layout.addView(plCanvas)
		self.views.append(plCanvas)
		
	def addMagPane(self):
		pass

	def addModel(self):
		pass

	def _mkStatusBar(self):
		playPauseButton = QtWidgets.QPushButton("Play/Pause")
		playPauseButton.clicked.connect(self._playPauseToggle)
		self.playPauseAction.triggered.connect(self._playPauseToggle)
		self.resetAction.triggered.connect(self._resetHelper)
		resetButton = QtWidgets.QPushButton("Reset")
		resetButton.clicked.connect(self._resetHelper)
		statusLabel = QtWidgets.QLabel()
		self.statusBar.addWidget(playPauseButton)
		self.statusBar.addWidget(resetButton)
		self.statusBar.addWidget(statusLabel)

	def openDialog(self,minimum,maximum,message):
		self.dialog = QProgressDialog(message,'Ok',minimum,maximum)
		self.progressBar_signal.connect(self.dialog.setValue)
		