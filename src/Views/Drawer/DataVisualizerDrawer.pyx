from Views.Drawer.Drawer cimport ImageDrawer
from pyqtgraph import QtCore, QtGui
cimport numpy as np 
import numpy as np 
from astropy.io import fits

cdef class DataVisualizerDrawer(ImageDrawer):

	def __init__(self,signal):
		ImageDrawer.__init__(self,signal)
		self.pixmap = []
		for i in range(0,255):
			self.pixmap.append(QtGui.qRgb(i,0,255-i))

	cpdef draw(self,object args):
		cdef np.ndarray[np.float64_t, ndim=2] data = np.array(args[0], dtype=np.float64)
		cdef double maxx = data.max()
		data *= 255.0/maxx
		formattedData = np.array(data,dtype=np.uint8)
		self.drawImage(formattedData)
