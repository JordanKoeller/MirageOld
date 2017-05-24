from Drawer cimport ImageDrawer
from pyqtgraph import QtCore, QtGui
cimport numpy as np 
import numpy as np 
cdef class DataVisualizerDrawer(ImageDrawer):

	def __init__(self,signal):
		ImageDrawer.__init__(self,signal)
		self.pixmap = []
		for i in range(0,255):
			self.pixmap.append(QtGui.qRgb(i,0,255-i))
	# cdef signal
	# cdef object pixmap
	# cdef object drawImage(self,np.ndarray[np.int8_t, ndim=2] pixels, object pixmap=*)

	# cdef object draw(self, object parameters, np.ndarray[np.int32_t, ndim=2] pixels)
	cpdef draw(self,object args):
		cdef np.ndarray[np.int32_t, ndim=2] data = args[0]
		cdef int maxx = data.max()
		print("Max = " + str(maxx))
		# for i in range(0,data.shape[0]):
		# 	for j in range(0,data.shape[1]):
		# 		print(data[i,j])
		data *= 255/maxx
		formattedData = np.array(data,dtype=np.uint8)
		self.drawImage(formattedData)
