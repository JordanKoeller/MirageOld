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
from .ParametersView import ParametersView
from .TableView import TableView
from .MagMapView import MagMapView
from .ViewLayout import ViewLayout
from .ModelDialog import ModelDialog
import factory
from app.Models import Model

class MainView(QtWidgets.QMainWindow,SignalRepo):
	"""

	"""

	playSignal = QtCore.pyqtSignal()
	pauseSignal = QtCore.pyqtSignal()
	resetSignal = QtCore.pyqtSignal()
	deactivateSignal = QtCore.pyqtSignal()
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
		#Set up menubar interraction
		self.playPauseAction.triggered.connect(self._playPauseToggle)
		self.resetAction.triggered.connect(self._resetHelper)
		# self.saveTableAction.triggered.connect(???)
		# self.loadTableAction.triggered.connect(???)
		# self.parametersEntryHelpAction.triggered.connect(???)
		self.actionAddCurvePane.triggered.connect(self.addCurvePane)
		self.actionAddImgPane.triggered.connect(self.addImgPane)
		self.actionAddMagPane.triggered.connect(self.addMagPane)
		self.actionAddParametersPane.triggered.connect(self.addParametersPane)
		self.actionAddTablePane.triggered.connect(self.addTablePane)
		# self.load_setup.triggered.connect(???)
		# self.save_setup.triggered.connect(???)
		# self.record_button.triggered.connect(???)
		self.visualizerViewSelector.triggered.connect(self.showVisSetup)
		self.queueViewSelector.triggered.connect(self.showTableSetup)
		self.tracerViewSelector.triggered.connect(self.showTracerSetup)
		self.actionConfigure_Models.triggered.connect(self.openModelDialog)

		self.parent = parent
		self.progressDialogSignal.connect(self.openDialog)
		self.canvasViews = []
		self.controller = None
		self.controllerViews = []
		self.isPlaying = False
		self.layout = ViewLayout(None,None)
		self.mainSplitter.addWidget(self.layout)
		self.initVisCanvas()
		self._mkStatusBar()

	def _playPauseToggle(self):
		print("Pressed")
		if self.isPlaying:
			self.isPlaying = False
			self.pauseSignal.emit()
			self.deactivateSignal.emit()
		else:
			paramters = self.parametersController.buildParameters()
			if paramters:
				Model.updateModel(paramters)
				self.controller = ControllerFactory(self.canvasViews,self.playSignal,self.pauseSignal,self.resetSignal,self.deactivateSignal)
				self.isPlaying = True
				self.playSignal.emit()

	def _resetHelper(self):
		self.isPlaying = False
		self.resetSignal.emit()
		for id,model in Model.items():
			model.reset()

	def initVisCanvas(self):
		self.addCurvePane()
		self.addImgPane()
		self.addParametersPane()

	def addImgPane(self):
		imgCanvas = LensedImageView()
		self.layout.addView(imgCanvas)
		self.canvasViews.append(imgCanvas)

	def addCurvePane(self):
		plCanvas = LightCurvePlotView()
		self.layout.addView(plCanvas)
		self.canvasViews.append(plCanvas)

	def addParametersPane(self):
		pv = ParametersView()
		self.parametersController = factory.ParametersControllerFactory(pv)
		self.layout.addView(pv)
		self.controllerViews.append(pv)
		return pv

	def addTablePane(self):
		tv = TableView()
		#Will need refactoring. TableControllerFactory is outdated
		self.tableViewController = factory.TableControllerFactory(tv,self.addParametersPane())
		self.layout.addView(tv)
		self.controllerViews.append(tv)
		
	def addMagPane(self):
		magCanvas = MagMapView()
		self.layout.addView(magCanvas)
		self.canvasViews.append(magCanvas)

	def addModel(self):
		pass

	def showVisSetup(self):
		self.layout.clear()
		self.addParametersPane()
		self.addCurvePane()
		self.addImgPane()

	def showTableSetup(self):
		self.layout.clear()
		self.addParametersPane()
		self.addTablePane()

	def showTracerSetup(self):
		self.layout.clear()
		self.addCurvePane()
		self.addImgPane()
		self.addMagPane()

	def _mkStatusBar(self):
		playPauseButton = QtWidgets.QPushButton("Play/Pause")
		playPauseButton.clicked.connect(self._playPauseToggle)
		resetButton = QtWidgets.QPushButton("Reset")
		resetButton.clicked.connect(self._resetHelper)
		statusLabel = QtWidgets.QLabel()
		self.statusBar.addWidget(playPauseButton)
		self.statusBar.addWidget(resetButton)
		self.statusBar.addWidget(statusLabel)

	def openDialog(self,minimum,maximum,message):
		self.dialog = QProgressDialog(message,'Ok',minimum,maximum)
		self.progressBar_signal.connect(self.dialog.setValue)

	def updateModels(self,model):
		print(model)
		Model.replaceModel(model)

	def openModelDialog(self):
		dialog = ModelDialog(self.canvasViews+self.controllerViews,self)
		dialog.show()
		dialog.accepted.connect(lambda: self.updateModels(dialog.exportModel()))
		