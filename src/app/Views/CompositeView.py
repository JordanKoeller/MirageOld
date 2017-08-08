from .View import CanvasView

class CompositePlot(CanvasView):
	"""View that holds other views inside. Using this enables merging of two plot views to display
	both data sets on one coordinate plane."""
	_colorKeys = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
	def __init__(self, *views):
		CanvasView.__init__(self,views[0].modelID, 'Composite View')
		self.type = 'Composite View'
		self._dataBin = []
		self._views = views[::-1]
		for view in self._views:
			view.disableUpdates()
			view.signal.connect(self.update)

		
	def update(self,data):
		self._dataBin.append(data)
		if len(self._dataBin) == len(self._views):
			self._plot.clear()
			for i in range(len(self._views)):
				data = self._dataBin[i]
				color = self._colorKeys[i%len(self._colorKeys)]
				self._plot.plot(data[0],data[1],clear=True,pen = {'width':5, 'color' :color})
			self._dataBin = []

	def addView(self,view):
		view.signal.connect(self.update)
		view.disableUpdates()
		self._views.append(view)

	@property
	def _plot(self):
		return self._views[0]._plot

class CompositeMagMap(CanvasView):
	"""View that holds multiple magmaps inside. Useful because allows for synchronizing 
	Tracers."""
	def __init__(self, *views):
		CanvasView.__init__(self,views[0].modelID, 'Composite View')
		self.type = 'Composite Mag Map'
		self._dataBin = []
		self._views = views[::-1]
		for view in self._views:
			view.disableUpdates()
			view.sigROISet.connect(self.update)

	def update(self,start,end):
		for i in range(len(self._views)):
			view = self._views[i]
			view.setROI(start,end)
		self._dataBin  = []

		