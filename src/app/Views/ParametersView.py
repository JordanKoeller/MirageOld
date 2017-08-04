from PyQt5 import uic, QtWidgets
from .. import parametersUIFile
from ..Utility.SignalRepo import SignalRepo
from .View import ControllerView

class ParametersView(ControllerView,SignalRepo):
	"""Wraps custom QtWidget with boxes/buttons for the user to specify 
	parameters of a system."""
	title = 'Parameters'
	def __init__(self,modelID='system_0',title=None):
		ControllerView.__init__(self,modelID,title)
		uic.loadUi(parametersUIFile,self)
		self.type = 'ParametersView'
