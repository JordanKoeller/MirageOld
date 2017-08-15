import sys

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QProgressDialog, QInputDialog
from PyQt5 import QtCore, QtWidgets

import factory

from .. import mainUIFile
from ..Utility import Vector2D
from ..Utility.SignalRepo import SignalRepo
from ..Controllers import ControllerFactory, ExportFactory
from .LensedImageView import LensedImageView
from .LightCurvePlotView import LightCurvePlotView
from .ParametersView import ParametersView
from .TableView import TableView
from .MagMapView import MagMapView
from .ViewLayout import ViewLayout
from .ModelDialog import ModelDialog
import factory
from app.Models import Model
from ..Controllers.ParametersController import ParametersController
from ..Controllers.QueueController import QueueController
from ..Controllers.FileManagerImpl import ParametersFileManager
from ..Models.MagnificationMapModel import MagnificationMapModel
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
		self.saveTableAction.triggered.connect(self.saveTable)
		self.loadTableAction.triggered.connect(self.loadTable)
		# self.parametersEntryHelpAction.triggered.connect(???)
		self.actionAddCurvePane.triggered.connect(self.addCurvePane)
		self.actionAddImgPane.triggered.connect(self.addImgPane)
		self.actionAddMagPane.triggered.connect(self.addMagPane)
		self.actionAddParametersPane.triggered.connect(self.addParametersPane)
		# self.actionAddTablePane.triggered.connect(self.addTablePane)
		self.save_setup.triggered.connect(self.saveSetup)
		self.load_setup.triggered.connect(self.loadSetup)
		# self.record_button.triggered.connect(???)
		self.visualizerViewSelector.triggered.connect(self.showVisSetup)
		self.queueViewSelector.triggered.connect(self.showTableSetup)
		self.tracerViewSelector.triggered.connect(self.showTracerSetup)
		self.actionConfigure_Models.triggered.connect(self.openModelDialog)
		self.actionExport.triggered.connect(self.exportLightCurves)

		self.parent = parent
		self.progressDialogSignal.connect(self.openDialog)
		self.controller = None
		self.modelControllers = []
		self.isPlaying = False
		self.layout = ViewLayout(None,None)
		self.layout.sigModelDestroyed.connect(self.removeModelController)
		self.mainSplitter.addWidget(self.layout)
		self.initVisCanvas()
		# self.addCurvePane()
		# self.addMagPane()
		self._mkStatusBar()

	def saveTable(self):
		tableController = self._findControllerHelper(QueueController)
		tableController.saveTable()

	def saveSetup(self):
		paramController = self._findControllerHelper(ParametersController)
		filer = ParametersFileManager()
		filer.open()
		filer.write(Model[paramController.modelID].parameters)

	def loadTable(self):
		tableController = self._findControllerHelper(QueueController)
		tableController.loadTable()

	def loadSetup(self):
		paramController = self._findControllerHelper(ParametersController)


	def _findControllerHelper(self,kind):
		ret = []
		for c in self.modelControllers:
			if isinstance(c,kind):
				ret.append(c)
		if len(ret) == 1:
			ret = ret[0]
		elif len(ret) == 0:
			ret = None
		else:
			model = QInputDialog.getItem(self,"Select Model",
				"Please Select a Model to save.",
				map(lambda i: i.modelID,filter(lambda v: isinstance(v,kind),self.modelControllers)))
			if model[1]:
				ret = next(filter(lambda i:i.modelID == model[0],self.modelControllers))
			else:
				ret = None
		return ret

	def _playPauseToggle(self):
		if self.isPlaying:
			self.isPlaying = False
			self.pauseSignal.emit()
			self.deactivateSignal.emit()
		else:
			for controllerView in self.modelControllers:
				parameters = controllerView.buildObject()
				if parameters:
					Model.updateModel(controllerView.modelID,parameters)
			self.controller = ControllerFactory(self.canvasViews,self.playSignal,self.pauseSignal,self.resetSignal,self.deactivateSignal)
			self.isPlaying = True
			self.playSignal.emit()

	def exportLightCurves(self):
		for controllerView in self.modelControllers:
			parameters = controllerView.buildObject()
			if parameters:
				Model.updateModel(controllerView.modelID,parameters)
		controller = ExportFactory(self.canvasViews,self.playSignal)
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

	def addCurvePane(self):
		plCanvas = LightCurvePlotView()
		self.layout.addView(plCanvas)

	def addParametersPane(self):
		pv = ParametersView()
		parametersController = factory.ParametersControllerFactory(pv)
		self.layout.addView(pv)
		self.modelControllers.append(parametersController)
		return parametersController

	def addTablePane(self,parametersController=None):
		tv = TableView()
		pc = parametersController or self.addParametersPane()
		#Will need refactoring. TableControllerFactory is outdated
		tableViewController = factory.TableControllerFactory(tv,pc)
		self.layout.addView(tv)
		self.modelControllers.append(tableViewController)
		
	def addMagPane(self):
		magCanvas = MagMapView()
		self.layout.addView(magCanvas)

	def showVisSetup(self):
		self.layout.clear()
		self.addParametersPane()
		self.addCurvePane()
		self.addImgPane()

	def showTableSetup(self):
		self.layout.clear()
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

	def removeModelController(self,view):
		removing = None
		for c in self.modelControllers:
			if c.view == view:
				removing = c
		if removing:
			self.modelControllers.remove(removing)

	def updateModels(self,model):
		# Model.replaceModel(model)
		pc = filter(lambda i: isinstance(i,ParametersController),self.modelControllers)
		for i in pc:
			i.bindFields(Model[i.modelID].parameters)
		for k,v in model.items():
			if isinstance(v,MagnificationMapModel):
				for view in self.canvasViews:
					if isinstance(view,MagMapView) and view.modelID == k:
						view.setMagMap(v.magMapArray,8.0)



	@property
	def canvasViews(self):
		return self.layout.canvasViews

	def openDialog(self,minimum,maximum,message):
		self.dialog = QProgressDialog(message,'Ok',minimum,maximum)
		self.progressBar_signal.connect(self.dialog.setValue)

	def openModelDialog(self):
		dialog = ModelDialog(self.canvasViews+[i.view for i in self.modelControllers],self)
		dialog.show()
		dialog.accepted.connect(lambda: self.updateModels(dialog.exportModel()))
