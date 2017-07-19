from PyQt5 import QtWidgets
import inspect 
from ...Models.Parameters.Parameters import Parameters

class HelpDialog(object):
	def __init__(self,parent):
		self.__dialog = QtWidgets.QErrorMessage(parent)
		self.__message = Parameters.__doc__ #NEEDTO UPDATE THIS

	def show(self):
		self.__dialog.showMessage(self.__message)


