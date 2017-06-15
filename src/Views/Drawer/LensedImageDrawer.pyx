import math
import numpy as np
from Utility.NullSignal import NullSignal
cimport numpy as np
import pyqtgraph as pg 
from pyqtgraph import QtCore, QtGui
from Calculator import ImageFinder
from Utility import Vector2D
from astropy import units as u
from Views.Drawer.Drawer cimport ImageDrawer
from Views.Drawer.ShapeDrawer cimport drawCircle, drawLine
import math
from astropy import constants as const
from scipy.cluster.vq import vq, kmeans, whiten


cdef class LensedImageDrawer(ImageDrawer):

	def __init__(self,signal=NullSignal):
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
		cdef np.ndarray[np.uint8_t, ndim=1] colors = self.getColorCode(pixels,parameters)
		for i in range(0,len(pixels)):
			canvas[pixels[i,0],pixels[i,1]] = colors[i]
		return self.drawImage(canvas,None)

	cdef getColorCode(self, np.ndarray[np.int32_t,ndim=2] pixels, object parameters):
		cdef x = np.array(pixels[:,0],dtype=np.float64) 
		cdef y = np.array(pixels[:,1],dtype=np.float64) 
		x = x - parameters.canvasDim /2
		y = y - parameters.canvasDim/2
		x = x*parameters.dTheta.to('arcsec').value
		y = y*parameters.dTheta.to('arcsec').value
		cdef double b = 4 * math.pi * (parameters.galaxy.velocityDispersion**2).to('km2/s2').value*(const.c** -2).to('s2/km2').value*parameters.dLS/parameters.quasar.angDiamDist
		b = u.Quantity(b,'rad').to('arcsec').value
		cdef double ptConst = (parameters.dLS/parameters.quasar.angDiamDist/parameters.galaxy.angDiamDist*4*const.G*const.c**-2).to('1/solMass').value
		cdef double gamSin = parameters.galaxy.shearMag*math.sin(2*(parameters.galaxy.shearAngle.to('rad').value - math.pi/2))
		cdef double gamCos = parameters.galaxy.shearMag*math.cos(2*(parameters.galaxy.shearAngle.to('rad').value - math.pi/2))
		sigma = np.zeros_like(x,np.float64)
		if parameters.galaxy.percentStars:
			starstuff = parameters.galaxy.stars
			for i in starstuff:
				dy = (y - i[1])**2
				dx = (x - i[0])**2
				sigma += (dy - dx)*i[2]/(dx + dy)**2
		cdef  x2 = b*y*y*(x*x+y*y)**(-3/2) + gamCos + ptConst*sigma
		cdef  y2 = b*x*x*(x*x+y*y)**(-3/2) - gamCos - ptConst*sigma
		cdef  xy = -b*x*y*(x*x+y*y)**(-3/2) + gamSin - 2*ptConst*sigma
		cdef  det = (1-x2)*(1-y2)-(xy)*(xy)
		cdef  trace = (1-x2)+(1-y2)
		cdef ret = np.ndarray((len(x2)),dtype=np.uint8)
		for i in range(0,len(x2)):
			if det[i] > 0.0 and trace[i] > 0:
				ret[i] = 1
			else:
				ret[i] = 5
		return ret
		
		
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
		drawCircle(int(parameters.canvasDim/2),int(parameters.canvasDim/2),r,canvas,3)

	def drawCritLines(self,pixels,parameters,canvas):
		pixels = whiten(pixels)
		imgs = kmeans(pixels,4)
		yInt = parameters.canvasDim/2
		yAx = parameters.canvasDim/2
		for i in imgs[0]:
			m = -i[0]/i[1]
			drawLine(int(parameters.canvasDim),m,0,canvas,3)



	cdef void __drawEinsteinRadius(self,np.ndarray[np.uint8_t,ndim=2] canvas,object parameters): 
		cdef int x0 = parameters.galaxy.center.x + parameters.canvasDim/2
		cdef int y0 = parameters.galaxy.center.y + parameters.canvasDim/2
		cdef int radius = parameters.einsteinRadius/parameters.dTheta.value
		drawCircle(x0,y0,radius, canvas,3)
