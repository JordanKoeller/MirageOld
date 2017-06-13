from pyqtgraph import QtCore, QtGui
cimport numpy as np
import numpy as np
import math 

cdef class Drawer(object):
	def __init__(self,signal):
		self.signal = signal
	cpdef draw(self, object args):
		pass

cdef class ImageDrawer(Drawer):

	def __init__(self,signal):
		Drawer.__init__(self,signal)
		self.pixmap = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66), QtGui.qRgb(53,252,92)]
		#Index 0: Black
		#Index 1: Yellow
		#Index 2: White
		#Index 3: Blue
		#Index 4: Orange
		#Index 5: Green
	cdef object drawImage(self,np.ndarray[np.uint8_t, ndim=2] pixels, object pixmap=None):
		if pixmap == None:
			pixmap = self.pixmap
		img = QtGui.QImage(pixels.tobytes(),pixels.shape[0],pixels.shape[1],QtGui.QImage.Format_Indexed8)
		img.setColorTable(pixmap)
		self.signal.emit(img)
		return img

	cpdef draw(self,object args):
		if len(args) > 1:
			self.drawImage(args[0],args[1])
		else:
			self.drawImage(args[0])

cdef class PlotDrawer(Drawer):

	def __init__(self,signal):
		Drawer.__init__(self,signal)
		self.reset()

	cdef append(self, double y, double x=-1):
		cdef np.ndarray[np.float64_t, ndim=1] replaceX
		cdef np.ndarray[np.float64_t, ndim=1] replaceY
		cdef int i
		if self.index < self.xAxis.shape[0]:
			self.yAxis[self.index] = y
			self.index += 1
		else:
			replaceX = np.arange(0,self.xAxis.shape[0]*2,dtype=np.float64)
			replaceY = np.zeros_like(replaceX,dtype=np.float64)
			for i in range(0,self.index):
				replaceY[i] = self.yAxis[i]
			self.yAxis = replaceY
			self.xAxis = replaceX
		self.signal.emit(np.asarray(self.xAxis),np.asarray(self.yAxis))

	cdef plotAxes(self, np.ndarray[np.float64_t, ndim=1] x, np.ndarray[np.float64_t, ndim=1] y):
		self.xAxis = x
		self.yAxis = y
		self.index = x.shape[0] - 1
		while (self.index > 0 and x[self.index] != 0):
			self.index -= 1
		if self.index == 0:
			self.index = x.shape[0] -1
		self.signal.emit(x,y)

	cpdef draw(self, object args):
		if len(args) == 1:
			self.append(args[0])
		else:
			x = args[0]
			y = args[1]
			if isinstance(y,float): ######Foreign to me, may be a bug source######
				self.append(y,x)
			else:
				self.plotAxes(x,y)

	def reset(self):
		self.xAxis = np.arange(0,1000,dtype=np.float64)
		self.yAxis = np.zeros_like(self.xAxis,dtype=np.float64)
		self.index = 0
# 		self.plotAxes(self.xAxis,self.yAxis)


cdef class CompositeDrawer:

	def __init__(self,imgDrawer, plotDrawer):
		self.imgDrawer = imgDrawer
		self.plotDrawer = plotDrawer

	cpdef draw(self, object imgArgs, object plotArgs):
		self.imgDrawer.draw(imgArgs)
		self.plotDrawer.draw(plotArgs)

	cpdef reset(self):
		self.plotDrawer.reset()