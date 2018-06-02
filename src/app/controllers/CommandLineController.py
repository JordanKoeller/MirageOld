from astropy import units as u

class CommandLineController(object):
	"""Controller that is spawned by the `visualizeMagMap` method in the
	`lens_analysis` module. It wraps the traditional model, view, controllers in one
	entity with convenience functions to manage visualizations of data
	generated in the past."""
	def __init__(self, trial,view,controller):
		super(CommandLineController, self).__init__()
		self._windowView = view
		self._masterController = controller
		self._trial = trial

	def show_curve(self,index,x_axis_unit='uas'):
		with u.add_enabled_units(self.model.parameters.specialUnits):
			controller = self._masterController
			curve = self._trial.lightcurves[index]
			curveParams = self._trial.parameters.getExtras('batch_lightcurve').bounding_box
			self._masterController.runner.plotFromLightCurve(controller,curve,x_axis_unit,curveParams)

	def getCurveOfRadius(self,index,radius,x_axis_unit='uas'):
		with u.add_enabled_units(self.model.parameters.specialUnits):
			calculationModel = calculationModel()

	@property
	def controller(self):
		return self._masterController

	@property
	def view(self):
		return self._windowView

	@property
	def model(self):
		return self._trial
	
	
		