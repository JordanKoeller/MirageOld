from .View import CanvasView, ViewBridge


# from .LightCurvePlotView import LightCurvePlotView
# from .MagMapView import MagMapView
class CompositePlot(ViewBridge):
	"""View that holds other views inside. Using this enables merging of two plot views to display
	both data sets on one coordinate plane."""
	_colorKeys = ['r', 'g', 'y', 'c', 'm', 'b', 'k', 'w']

	def __init__(self, *views):
		views[len(views)-1]._plot.addLegend()
		ViewBridge.__init__(self,*views)
		self.type = 'Composite View'
		
	def update(self,data):
		self._dataBin.append(data)
		if len(self._dataBin) == len(self._views):
			self._plotView.clear()
			for i in range(len(self._views)):
				data = self._dataBin[i]
				color = self._colorKeys[i%len(self._colorKeys)]
				if len(self._plotView.legend.items) < len(self._views):
					self._plotView.plot(data[0],data[1],clear=False, pen = {'width':5, 'color' :color}, name = 'Model = '+self._views[i].modelID)
				else:
					self._plotView.plot(data[0],data[1],clear=False, pen = {'width':5, 'color' :color})
			self._dataBin = []

	def addView(self,view):
		ViewBridge.addView(self,view)
		if self._views and self._plotView.legend:
			for view in self._views:
				self._plotView.legend.removeItem('Model = '+view.modelID)

	@property
	def _plotView(self):
		return self._views[0]._plot

class CompositeMagMap(ViewBridge):
	"""View that holds multiple magmaps inside. Useful because allows for synchronizing 
	Tracers."""
	def __init__(self, *views):
		ViewBridge.__init__(self,*views)
		self.type = 'Composite Mag Map'

	def update(self,start,end):
		for i in range(len(self._views)):
			view = self._views[i]
			view.setROI(start,end)
		self._dataBin  = []

	def addView(self, view):
		# if isinstance(view,self._DTYPE):
		# view.disablepdates()
		view.sigROISet.connect(self.update)
		self._views.append(view)
		view.setBridge(self)
