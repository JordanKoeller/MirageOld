import copy

_engineRef = None

def _getOrCreateEngine():
	from mirage.engine import getCalculationEngine
	global _engineRef
	if not _engineRef:
		_engineRef = getCalculationEngine()



class EngineDelegate(object):
	"""A container for communicating with an engine for on-the-fly calculation.
	This allows for a shared engine between Trials, to prevent redundant recalculation
	of data."""
	def __init__(self,parameters=None):
		super(EngineDelegate, self).__init__()
		_getOrCreateEngine()
		if parameters:
			self.reconfigure(parameters)

		#TODO: Put classmethods for fromFile or fro

	@property
	def engine(self):
		global _engineRef
		return _engineRef

	def bind_trial(self,trial):
		from .Trial import Trial
		if isinstance(trial, Trial):
			self.reconfigure(trial.parameters)
		else:
			self.reconfigure(trial)
	

	def reconfigure(self,parameters,force_recalculate = False):
		paramcopy = copy.deepcopy(parameters)
		self.engine.update_parameters(parameters)
		if force_recalculate:
			self.engine.reconfigure()


	def query_point(self,x,y,r):
		return self.engine.query_line([[x,y]],r)

	def query_line(self,pts,r=None):
		return self.engine.query_line(pts,r)

	def query_light_curves(self,pts,r=None):
		values = self.engine.calculation_delegate.sample_light_curves(pts,r)
		return self.engine.normalize_magnification(values,r)

	def query_area(self,area,radius=None):
		return self.engine.make_mag_map(area.center,area.dimensions,area.resolution,radius)




		