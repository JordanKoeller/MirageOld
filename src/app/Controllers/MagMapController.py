from .GUIController import GUIController

class MagMapController(GUIController):
	"""docstring for MagMapController"""



	def __init__(self, view):
		GUIController.__init__(self,view)

	def bindFields(self):
		from ..Models import Model
		self.view.setMagMap(Model[self.modelID].magMapArray)

	def setModel(self,model):
# 		if isinstance(model,la.Trial):
		from ..Models.MagnificationMapModel import MagnificationMapModel
		from ..Models import Model
		self.view._modelID = model.filename
		Model[self.modelID] = MagnificationMapModel(model)
		self.bindFields()
# 		else:
# 			raise ValueError("model must be of type Trial")


