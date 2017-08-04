import copy

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QInputDialog

from .. import modeldialogUIFile
from pyqtgraph.widgets.TableWidget import TableWidget
from .ViewTable import ViewTable
from ..Models import Model
# from ..Controller.ModelFileManager import ModelFileManager

class ModelDialog(QDialog):
	"""provides a dialog for editing the models associated with the 
	simulator."""
	def __init__(self,views,parent=None):
		QDialog.__init__(self,parent)
		uic.loadUi(modeldialogUIFile,self)
		self._viewTable = ViewTable()
		self.horizontalLayout.insertWidget(1,self._viewTable)
		self.setModelList(Model)
		self._viewTable.loadViews(views)
		self.modelList.itemClicked.connect(self.setSelectedModel)
		self.addModelButton.currentIndexChanged.connect(self.addModel)
		self._selected = None

	def setModelList(self,models):
		self._models = models
		self._updateModelList()

	def _updateModelList(self):
		self.modelList.clear()
		for k,v in self._models.items():
			item = QListWidgetItem(k)
			item.model = v
			item.modelID = k
			self.modelList.addItem(item)


	def setSelectedModel(self,item):
		if self._selected:
			selected = self._viewTable.selectedViews
			deselected = self._viewTable.deselectedViews
			for view in selected:
				view.modelID = self._selected.modelID
			for view in deselected:
				if view.modelID == self._selected.modelID:
					view.modelID = ''
		self._selected = item
		self._viewTable.selectModel(item.modelID)

	def addModel(self,source):
		self.addModelButton.setCurrentIndex(0)
		if source == 1:
			#Means from File
			modelLoader = ModelFileManager()
			model = model.load()
		elif source == 2:
			#Means from scratch
			name,success = QInputDialog.getText(self,"Add Model","Enter a name for the new model")
			if success:
				model = Model.DefaultModel()
				model.modelID = name
				self._models[name] = model
				self._updateModelList()

	def exportModel(self):
		print(self._models)
		print("Done printing")
		return self._models
		# return copy.deepcopy(self._models)