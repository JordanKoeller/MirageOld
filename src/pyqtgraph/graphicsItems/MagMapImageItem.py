from PyQt5 import QtCore
from .ImageItem import ImageItem
class MagMapImageItem(ImageItem):
	"""Extends ImageItem with its own mousePressEvent, mouseDragEvent, and mouseReleaseEvent methods to handle click-and-drag production
	of linear ROI objects.

	Any initialization parameters passed in are passed on to ImageItem.

	Intercepts RightClick MouseEvents and sends them on with the three signals

	sigPressed(QtCore.QPoint) of where the mouse event occurred.
	sigDragged(QtCore.QPoint) of where the mouse event occurred.
	sigReleased(QtCore.QPoint) of where the mouse event occurred."""

	sigPressed = QtCore.pyqtSignal(object)
	sigDragged = QtCore.pyqtSignal(object)
	sigReleased = QtCore.pyqtSignal(object)

	def __init__(self, *args, **kwargs):
		ImageItem.__init__(self,*args,**kwargs)
		self.dragStarted = False


	def mousePressEvent(self,ev):
		if ev.button() == QtCore.Qt.RightButton:
			ev.accept()
			self.dragStarted = True
			self.sigPressed.emit(ev.pos())
		else:
			ImageItem.mousePressEvent(self,ev)

	def mouseMoveEvent(self,ev):
		if self.dragStarted:
			self.sigDragged.emit(ev.pos())
			ev.accept()
		else:
			ImageItem.mouseMoveEvent(self,ev)
	def mouseReleaseEvent(self,ev):
		if ev.button() == QtCore.Qt.RightButton:
			ev.accept()
			self.dragStarted = False
			self.sigReleased.emit(ev.pos())
		else:
			ImageItem.mouseMoveEvent(self,ev)