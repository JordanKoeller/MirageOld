
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from pyqtgraph import RectROI
from .View import CanvasView

class LensedImageView(CanvasView):
	"""docstring for LensedImageView"""
	def __init__(self, modelID='default',title=None):
		CanvasView.__init__(self,modelID,title,)
		self._viewBox = self.addViewBox(lockAspect=True)
		self._viewBox.invertY()
		self._imgItem = ImageItem()
		self._viewBox.addItem(self._imgItem)
		self.title = "Lensed Image"
		self.type = "ImageView"
		self._signalRef.connect(self.setImage)

	def setImage(self,img,*args,**kwargs):
		self._imgItem.setImage(img)

	def placeTracer(self,xy):
		self._tracer = RectROI(xy)
		
	def update(self, *args, **kwargs):
		self.setImage(*args,**kwargs)

	# def getSelectedRegion(self):
	# 	if self._tracer:
	# 		#TBD
	
	
