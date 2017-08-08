
from .. import lens_analysis as la
from ..Calculator.Engine.Engine_MagMap import Engine_MagMap


class MagnificationMapModel(object):
	"""Model Implimentation for magnification map data. Must be generated from a .dat data file,
	which contains MagMap data."""
	def __init__(self, trial):
		magmap, parameters = trial.traceQuasar()
		mmp = parameters.extras.getParams('magmap')
		self._Engine = Engine_MagMap(parameters,mmp,magmap)

	def reset(self):
		self.parameters.quasar.setTime(0)


	@property
	def parameters(self):
		return self._Engine.parameters

	@property
	def magMapArray(self):
		return self._Engine.magMapArray

	@property
	def magMapParameters(self):
		return self._Engine.magMapParameters

	@property
	def trial(self):
		return la.load(self.fileName)[trialNo]

	@property
	def engine(self):
		return self._Engine