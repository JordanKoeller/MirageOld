from .View import CanvasView
from .LightCurvePlotView import LightCurvePlotView
from .MagMapView import MagMapView


class CompositeView(object):
	def __init__(self,*views):
		self._views = []
		self._dataBin = []
		for view in views[::-1]:
			self.addView(view)

	def addView(self,view):
		if isinstance(view,self._DTYPE):
			view.signal.connect(self.update)
			view.disableUpdates()
			self._views.append(view)

	def update(self,data):
		pass

class CompositePlot(LightCurvePlotView,CompositeView):
	"""View that holds other views inside. Using this enables merging of two plot views to display
	both data sets on one coordinate plane."""
	_colorKeys = ['r', 'g', 'y', 'c', 'm', 'b', 'k', 'w']

	def __init__(self, *views):
		self._DTYPE = LightCurvePlotView
		LightCurvePlotView.__init__(self,views[0].modelID, 'Composite View')
		CompositeView.__init__(self,*views)
		self.type = 'Composite View'
		
	def update(self,data):
		self._dataBin.append(data)
		if len(self._dataBin) == len(self._views):
			self._plotView.clear()
			for i in range(len(self._views)):
				data = self._dataBin[i]
				color = self._colorKeys[i%len(self._colorKeys)]
				self._plotView.plot(data[0],data[1],clear=False, pen = {'width':5, 'color' :color})
			self._dataBin = []

	@property
	def _plotView(self):
		return self._views[0]._plot

class CompositeMagMap(MagMapView,CompositeView):
	"""View that holds multiple magmaps inside. Useful because allows for synchronizing 
	Tracers."""
	def __init__(self, *views):
		self._DTYPE = MagMapView
		MagMapView.__init__(self,views[0].modelID, 'Composite View')
		CompositeView.__init__(self,*views)
		self.type = 'Composite Mag Map'

	def update(self,start,end):
		for i in range(len(self._views)):
			view = self._views[i]
			view.setROI(start,end)
		self._dataBin  = []

	def addView(self, view):
		if isinstance(view,self._DTYPE):
			view.disableUpdates()
			view.sigROISet.connect(self.update)
			self._views.append(view)