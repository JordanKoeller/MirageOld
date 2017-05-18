import math
import numpy as np
cimport numpy as np
from Graphics import Plot
import pyqtgraph as pg 
from pyqtgraph import QtCore, QtGui
from Calculator import ImageFinder
from Utility import Vector2D
from astropy import constants as const
from Drawer cimport ImageDrawer

cdef class LensedImageDrawer(ImageDrawer):

	def __init__(self,signal):
		ImageDrawer.__init__(self,signal)
	cpdef draw(self,object args):
		cdef object parameters = args[0]
		cdef np.ndarray[np.int32_t, ndim=2] pixels = args[1]
		cdef np.ndarray[np.uint8_t, ndim=2] canvas = np.zeros((parameters.canvasDim,parameters.canvasDim), dtype=np.uint8)
		if parameters.displayGalaxy:
			parameters.galaxy.drawGalaxy(canvas,parameters)
		if parameters.displayStars:
			parameters.galaxy.drawStars(canvas,parameters)
		if parameters.displayQuasar:
			parameters.quasar.draw(canvas,parameters)
		cdef int pixel = 0
		cdef int end = pixels.shape[0]
		with nogil:
			for pixel in range(0,end):
				canvas[pixels[pixel,0],pixels[pixel,1]] = 1
# 		self.__drawEinsteinRadius(canvas,parameters)
# 		self.__drawEinsteinRadius(canvas,parameters)
# 		self.__drawEinsteinRadius(canvas,parameters)
		# self.__drawTrackers(parameters,canvas)
		return self.drawImage(canvas,None)
		
		
	cdef void __drawTrackers(self,np.ndarray[np.uint8_t,ndim=2] canvas, object parameters): #*************NOT OPTIMIZED **************
		x = ImageFinder.getRoot(-1,-1,parameters)
		xNorm = x
		xInt = Vector2D(int(xNorm.x),int(xNorm.y))
		for i in range(-1,1):
			for j in range(-1,1):
				canvas[i+xInt.x+ int(parameters.canvasDim/2)][int(parameters.canvasDim/2) - (j+xInt.y)] = 3

	cdef void __drawEinsteinRadius(self,np.ndarray[np.uint8_t,ndim=2] canvas,object parameters): #***************NOT OPTIMIZED****************
		x0 = parameters.galaxy.center.x + 400
		y0 = parameters.galaxy.center.y + 400
		# radius = parameters.einsteinRadius/math.sqrt(math.pi)
		radius = parameters.galaxy.shearMag
		# radius = (4*math.pi*parameters.galaxy.velocityDispersion**2/(const.c.to('km/s')**2)).value - parameters.galaxy.shearMag*4.84814e-6
		x = abs(radius/parameters.dTheta.value)
		y = 0
		err = 0
		while x >= y:
			if x0 + x > 0 and y0 + y > 0 and x0 + x < parameters.canvasDim and y0 + y < parameters.canvasDim:
					canvas[int(x0 + x), int(y0 + y)] = 3
			if x0 + y > 0 and y0 + x > 0 and x0 + y < parameters.canvasDim and y0 + x < parameters.canvasDim:
					canvas[int(x0 + y), int(y0 + x)] = 3
			if x0 - y > 0 and y0 + x > 0 and x0 - y < parameters.canvasDim and y0 + x < parameters.canvasDim:
					canvas[int(x0 - y), int(y0 + x)] = 3
			if x0 - x > 0 and y0 + y > 0 and x0 - x < parameters.canvasDim and y0 + y < parameters.canvasDim:
					canvas[int(x0 - x), int(y0 + y)] = 3
			if x0 - x > 0 and y0 - y > 0 and x0 - x < parameters.canvasDim and y0 - y < parameters.canvasDim:
					canvas[int(x0 - x), int(y0 - y)] = 3
			if x0 - y > 0 and y0 - x > 0 and x0 - y < parameters.canvasDim and y0 - x < parameters.canvasDim:
					canvas[int(x0 - y), int(y0 - x)] = 3
			if x0 + y > 0 and y0 - x > 0 and x0 + y < parameters.canvasDim and y0 - x < parameters.canvasDim:
					canvas[int(x0 + y), int(y0 - x)] = 3
			if x0 + x > 0 and y0 - y > 0 and x0 + x < parameters.canvasDim and y0 - y < parameters.canvasDim:
					canvas[int(x0 + x), int(y0 - y)] = 3
			if err <= 0:
				y += 1
				err += 2*y + 1
			if err > 0:
				x -= 1
				err -= 2*x + 1
