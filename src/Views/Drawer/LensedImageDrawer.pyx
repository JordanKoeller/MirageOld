import math
import numpy as np
cimport numpy as np
import pyqtgraph as pg 
from pyqtgraph import QtCore, QtGui
from Calculator import ImageFinder
from Utility import Vector2D
from astropy import constants as const
from Views.Drawer.Drawer cimport ImageDrawer
from Views.Drawer.ShapeDrawer cimport ShapeDrawer
import math
from astropy import constants as const
from scipy.cluster.vq import vq, kmeans, whiten


cdef class LensedImageDrawer(ImageDrawer):

	def __init__(self,signal):
		ImageDrawer.__init__(self,signal)
		self.__shapeDrawer = ShapeDrawer(signal)

	
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
# 		if end > 1:
# 			with nogil:
# 				for pixel in range(0,end):
# 					canvas[pixels[pixel,0],pixels[pixel,1]] = 1
		for i in pixels:
			canvas[i[0],i[1]] = 1
		# self.drawCriticalRadius(canvas,parameters)
		# self.drawCritLines(pixels,parameters,canvas)
		return self.drawImage(canvas,None)
		
		
	cdef void __drawTrackers(self,np.ndarray[np.uint8_t,ndim=2] canvas, object parameters): #*************NOT OPTIMIZED **************
		x = ImageFinder.getRoot(-1,-1,parameters)
		xNorm = x
		xInt = Vector2D(int(xNorm.x),int(xNorm.y))
		for i in range(-1,1):
			for j in range(-1,1):
				canvas[i+xInt.x+ int(parameters.canvasDim/2)][int(parameters.canvasDim/2) - (j+xInt.y)] = 3

	def drawCriticalRadius(self,canvas,parameters):
		nu = 2*(parameters.galaxy.shearAngle.to('rad').value - parameters.quasar.position.angle)
		b = (4*math.pi*(parameters.galaxy.velocityDispersion/const.c)**2)*parameters.dLS/parameters.quasar.angDiamDist
		beta = parameters.quasar.position.magnitude()
		r = (b - beta)/(1+parameters.galaxy.shearMag*math.cos(nu))
		r /= parameters.dTheta.value
		self.__shapeDrawer.drawCircle(int(parameters.canvasDim/2),int(parameters.canvasDim/2),r,canvas)

	def drawCritLines(self,pixels,parameters,canvas):
		pixels = whiten(pixels)
		imgs = kmeans(pixels,4)
		yInt = parameters.canvasDim/2
		yAx = parameters.canvasDim/2
		for i in imgs[0]:
			m = -i[0]/i[1]
			self.__shapeDrawer.drawLine(int(parameters.canvasDim),m,0,canvas)



	cdef void __drawEinsteinRadius(self,np.ndarray[np.uint8_t,ndim=2] canvas,object parameters): 
		cdef int x0 = parameters.galaxy.center.x + parameters.canvasDim/2
		cdef int y0 = parameters.galaxy.center.y + parameters.canvasDim/2
		cdef int radius = parameters.einsteinRadius/parameters.dTheta.value
		self.__drawCircle(x0,y0,radius, canvas)
