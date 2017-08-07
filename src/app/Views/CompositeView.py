from .View import CanvasView

class CompositeView(CanvasView):
	"""View that holds other views inside. Using this enables merging of two plot views to display
	both data sets on one coordinate plane."""
	def __init__(self, *views):
		CanvasView.__init__(self,views[0].modelID, 'Composite View')
		self.type = 'Composite View'
		self._dataBin = []
		self._views = views
		for view in self._views:
			view.signal.connect(self.update)

		
	def update(self,data):
		self._dataBin.append(data)
		if len(self._dataBin) == len(self._views):
			data1 = self._dataBin[0]
			data2 = self._dataBin[1]
			self._plot.plot(data1[0],data1[1],clear=True,pen = {'width':5, 'color' :'r'})
			self._plot.plot(data2[0],data2[1],clear=False,pen = {'width':5, 'color': 'b'})
			self._dataBin = []

	def addPlot(self,plot):
		plot.signal.connect(self.update)
		plot.disableUpdate()
		self._views.append(plot)

	@property
	def _plot(self):
		return self._views[0]._plot