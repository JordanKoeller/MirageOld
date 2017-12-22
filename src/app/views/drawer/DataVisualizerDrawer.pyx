from .Drawer cimport ImageDrawer
from astropy.io import fits

import numpy as np 
from pyqtgraph import QtCore, QtGui

from ...Utility.NullSignal import NullSignal


cimport numpy as np 

cdef class DataVisualizerDrawer(ImageDrawer):

	def __init__(self,signal=NullSignal):
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
