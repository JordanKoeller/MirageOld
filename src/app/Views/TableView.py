from PyQt5 import uic

from .. import tableUIFile
from .ExperimentQueueTable import ExperimentQueueTable
from .View import ControllerView


class TableView(ControllerView):
	"""Wraps a custom QtWidget to make a experiment table for setting up batch runs."""
	def __init__(self,modelID='default',title='Table View'):
		ControllerView.__init__(self,modelID,title)
		uic.loadUi(tableUIFile,self)
		self.__initTable()
		self.type = 'TableView'

	def __initTable(self):
		self.table = ExperimentQueueTable(self.scrollAreaWidgetContents,editable = False)
	
	def addExperiment(self,*args,**kwargs):
		self.table.addExperiment(*args,**kwargs)

	def updateExperiement(self,*args,**kwargs):
		self.table.updateExperiement(*args,**kwargs)

	def clearTable(self):
		self.table.clearTable()

	@property
	def experiments(self):
		return self.table.experiments	