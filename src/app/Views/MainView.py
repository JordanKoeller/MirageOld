
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QInputDialog

from app.Models import Model
# import factory

# from .. import mainUIFile
# from ..Controllers import ControllerFactory, ExportFactory
from ..Controllers.FileManagerImpl import ParametersFileManager, ParametersFileReader
from ..Controllers.ParametersController import ParametersController
from ..Controllers.QueueController import QueueController
# from ..Models.MagnificationMapModel import MagnificationMapModel
# from .LensedImageView import LensedImageView
# from .LightCurvePlotView import LightCurvePlotView
# from .MagMapView import MagMapView
# from .ModelDialog import ModelDialog
# from .ParametersView import ParametersView
# from .TableView import TableView
from .ViewLayout import ViewLayout
from .WindowFrame import WindowFrame


# from ..Controllers import GlobalsController
class MainView(WindowFrame):
	"""

	"""

	def __init__(self, area=None,parent=None):
		super(MainView, self).__init__()
#		 uic.loadUi(mainUIFile, self)
#		 self.addSignals(progressLabel=self.progressLabelSignal,
#						 play=self.playSignal,
#						 pause=self.pauseSignal,
#						 reset=self.resetSignal,
#						 progressDialog=self.progressDialogSignal
#						 )
		self.recordingFileManager = None
		self.setCenter(area)
# 
#		 # Set up menubar interraction
		
		self.parent = parent
# 		self.progressDialogSignal.connect(self.openDialog)
		self.controller = None
		self.isPlaying = False
		self.layout = ViewLayout(None, None)
		self.layout.sigModelDestroyed.connect(self.removeModelController)
		self.mainSplitter.addWidget(self.layout)
		self.save_setup.triggered.connect(self.saveSetup)
		self.load_setup.triggered.connect(self.loadSetup)
		self.saveTableAction.triggered.connect(self.saveTable)
		self.loadTableAction.triggered.connect(self.loadTable)


	def saveTable(self):
		tableController = self._findControllerHelper(QueueController)
		tableController.saveTable()

	def saveSetup(self):
		paramController = self._findControllerHelper(ParametersController)
		filer = ParametersFileManager()
		if filer.open():
			filer.write(Model[paramController.modelID].parameters)

	def loadTable(self):
		tableController = self._findControllerHelper(QueueController)
		tableController.loadTable()

	def loadSetup(self):
		paramController = self._findControllerHelper(ParametersController)
		loader = ParametersFileReader()
		if loader.open():
			params = loader.load()
			paramController.paramSetter_signal.emit(params)

	def _findControllerHelper(self, kind):
		ret = []
		for c in self.modelControllers:
			if isinstance(c, kind):
				ret.append(c)
		if len(ret) == 1:
			ret = ret[0]
		elif len(ret) == 0:
			ret = None
		else:
			model = QInputDialog.getItem(self, "Select Model",
				"Please Select a Model to save.",
				map(lambda i: i.modelID, filter(lambda v: isinstance(v, kind), self.modelControllers)))
			if model[1]:
				ret = next(filter(lambda i:i.modelID == model[0], self.modelControllers))
			else:
				ret = None
		return ret

	def _mkStatusBar(self):
		playPauseButton = QtWidgets.QPushButton("Play/Pause")
		playPauseButton.clicked.connect(self._playPauseToggle)
		resetButton = QtWidgets.QPushButton("Reset")
		resetButton.clicked.connect(self._resetHelper)
		statusLabel = QtWidgets.QLabel()
		self.statusBar.addWidget(playPauseButton)
		self.statusBar.addWidget(resetButton)
		self.statusBar.addWidget(statusLabel)

	def removeModelController(self, view):
		removing = None
		for c in self.modelControllers:
			if c.view == view:
				removing = c
		if removing:
			self.modelControllers.remove(removing)

	def closeEvent(self,*args,**kwargs):
		# self.centralWidget.clear()
		print("Closing")
		self.layout.clear()
		QtGui.QMainWindow.closeEvent(self,*args,**kwargs)
		
	def addView(self,view):
		self.layout.addView(view)
		
	# def findController(self,modelID,controllerType):
	#     ret = []
	#     for c in modelControllers():
	#         if isinstance(c,controllerType) and c.modelID == modelID:
	#             ret.append(c)
	#     return ret

	# def _findView(modelID,windowType):
	#     ret = []
	#     for v in canvasViews():
	#         if isinstance(v,windowType) and v.modelID == modelID:
	#             ret.append(v)
	#     return ret


	@property
	def views(self):
		return self.layout.views
