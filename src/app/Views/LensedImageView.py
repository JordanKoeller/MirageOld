
from pyqtgraph import RectROI
from pyqtgraph.graphicsItems.ImageItem import ImageItem

from .View import CanvasView
from PyQt5 import QtCore

class LensedImageView(CanvasView):
	"""docstring for LensedImageView"""

	sigPressed = QtCore.pyqtSignal(object)
	sigDragged = QtCore.pyqtSignal(object)
	sigReleased = QtCore.pyqtSignal(object)

	def __init__(self, modelID='default',title=None):
		CanvasView.__init__(self,modelID,title,)
		self._viewBox = self.addViewBox(lockAspect=True)
		self._viewBox.invertY()
		self._imgItem = ImageItem()
		self._viewBox.addItem(self._imgItem)
		# self.title = "Lensed Image"
		self.type = "ImageView"
		self.dragStarted = False

	def mousePressEvent(self,ev):
		if ev.button() == QtCore.Qt.RightButton:
			print("Right Clicked")
			ev.accept()
			self.dragStarted = True
			self.sigPressed.emit(ev.pos())
		else:
			CanvasView.mousePressEvent(self,ev)

	def mouseMoveEvent(self,ev):
		if self.dragStarted:
			self.sigDragged.emit(ev.pos())
			ev.accept()
		else:
			CanvasView.mouseMoveEvent(self,ev)

	def mouseReleaseEvent(self,ev):
		if ev.button() == QtCore.Qt.RightButton:
			ev.accept()
			self.dragStarted = False
			self.sigReleased.emit(ev.pos())
		else:
			CanvasView.mouseMoveEvent(self,ev)

	def setImage(self,img,*args,**kwargs):
		self._imgItem.setImage(img)

	def placeTracer(self,xy):
		self._tracer = RectROI(xy)
		
	def update(self, *args, **kwargs):
		self.setImage(*args,**kwargs)

	# def getSelectedRegion(self):
	# 	if self._tracer:
	# 		#TBD
	
	
