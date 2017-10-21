from .GUIController import GUIController

class MagMapController(GUIController):
	"""docstring for MagMapController"""



	def __init__(self, view):
		GUIController.__init__(self,view)

	def bindFields(self,mm,):
		from ..Models import Model
		self.view.setMagMap(Model[self.modelID].magMapArray)
