

class CurveDataFileManager(QtCore.QThread):
	"""Handles saving magnification curves. Can save 1 or many, with various statistical processes applied."""
	def __init__(self, filename):
		super(CurveDataFileManager, self).__init__()
		self.filename = filename
		self.counter = 0
		self.cache = "../../cache/run"

	def addRun(self,x,y):
		#Can use numpy's file api here
		with open(self.cache + str(counter), "wb+") as file:

