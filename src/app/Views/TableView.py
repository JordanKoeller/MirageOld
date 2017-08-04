from PyQt5 import uic
from .. import tableUIFile
from .View import ControllerView
from .ExperimentQueueTable import ExperimentQueueTable
class TableView(ControllerView):
	"""Wraps a custom QtWidget to make a experiment table for setting up batch runs."""
	def __init__(self,modelID='system_0',title='Table View'):
		ControllerView.__init__(self,modelID,title)
		uic.loadUi(tableUIFile,self)
		self.__initTable()
		self.type = 'TableView'

	def __initTable(self):
		self.table = ExperimentQueueTable(self.scrollAreaWidgetContents,editable = False)
	