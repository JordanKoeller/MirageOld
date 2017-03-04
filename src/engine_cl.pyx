# distutils: language=c++
# cython: profile=True
from __future__ import division
import numpy as np
cimport numpy as np
from WrappedTree_old import WrappedTree
from stellar import Galaxy
from stellar import Quasar
from Configs import Configs 
from astropy.cosmology import WMAP7 as cosmo
from Vector2D import Vector2D
from Vector2D import zeroVector
import time
from astropy import constants as const
from astropy import units as u
import math
import pyopencl as cl
import pyopencl.tools
import os
from SpatialTree cimport SpatialTree, Pixel
from libcpp.vector cimport vector
import random
from PyQt5 import QtGui, QtCore
import cython
cimport engineHelper
import ctypes
from libc.math cimport sin, cos, atan2, sqrt



cdef packed struct lenser_struct:
	np.int32_t lenserType
	np.float64_t mass
	np.float64_t x
	np.float64_t y
	np.float64_t radius


cdef class Engine_cl:

	def __init__(self,quasar,galaxy,configs, auto_configure = True):
		self.__quasar = quasar
		self.__galaxy = galaxy
		self.__configs = configs
		self.__preCalculating = False
		self.__needsReconfiguring = True
		self.time = 0.0
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')
		self.__calcER()
		self.__galaxy.generateStars(self.configs)
		# self.__trueLuminosity = math.pi * (self.__quasar.radius.value/self.__configs.dTheta)**2
		self.img = QtGui.QImage(self.__configs.canvasDim,self.__configs.canvasDim, QtGui.QImage.Format_Indexed8)
		self.__imgColors = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66)]
		self.img.setColorTable(self.__imgColors)
		self.img.fill(0)
		if auto_configure:
			self.reconfigure()

	@property
	def configs(self):
		return self.__configs

	@property
	def galaxy(self):
		return self.__galaxy

	@property
	def quasar(self):
		return self.__quasar

	@property
	def einsteinRadius(self):
		return self.__einsteinRadius

	@property
	def needsReconfiguring(self):
		return self.__needsReconfiguring

	def ray_trace(self, use_GPU = False):
		return self.ray_trace_gpu(False)

	def drawEinsteinRadius(self,canvas,radius,centerx,centery):
		cdef int x0, y0
		x0 = centerx
		y0 = centery
		cdef int x = radius/self.configs.dTheta
		cdef int y = 0
		cdef int err = 0
		while x >= y:
			canvas.setPixel(x0 + x, y0 + y,1)
			canvas.setPixel(x0 + y, y0 + x,1)
			canvas.setPixel(x0 - y, y0 + x,1)
			canvas.setPixel(x0 - x, y0 + y,1)
			canvas.setPixel(x0 - x, y0 - y,1)
			canvas.setPixel(x0 - y, y0 - x,1)
			canvas.setPixel(x0 + y, y0 - x,1)
			canvas.setPixel(x0 + x, y0 - y,1)
			if err <= 0:
				y += 1
				err += 2*y + 1
			if err > 0:
				x -= 1
				err -= 2*x + 1

	cdef ray_trace_gpu(self,use_GPU):
		print(self.einsteinRadius)
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		if use_GPU:
			os.environ['PYOPENCL_CTX'] = '0:1'
		else:
			os.environ['PYOPENCL_CTX'] = '0:0'
		cdef int height = self.__configs.canvasDim
		cdef int width = self.__configs.canvasDim
		cdef np.float64_t dTheta = self.__configs.dTheta
		cdef np.ndarray result_nparray_x = np.ndarray((width,height), dtype = np.float64)
		cdef np.ndarray result_nparray_y = np.ndarray((width,height), dtype = np.float64)
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__galaxy.getStarArray()

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

		# create buffers to send to device
		mf = cl.mem_flags		
		#input buffers
		stars_buffer_mass = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray_mass)
		stars_buffer_x = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray_x)
		stars_buffer_y = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray_y)
		#output buffers
		result_buffer_x = cl.Buffer(context, mf.READ_WRITE, result_nparray_x.nbytes)
		result_buffer_y = cl.Buffer(context, mf.READ_WRITE, result_nparray_y.nbytes)

		# read and compile opencl kernel
		prg = cl.Program(context, open('engine_helper.cl').read()).build()
		prg.ray_trace(queue,(width,height),None,
			stars_buffer_mass,
			stars_buffer_x,
			stars_buffer_y,
			np.int32(len(stars_nparray_x)),
			np.float64((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
			np.float64(4*math.pi*(const.c**-2).to('s2/km2').value),
			np.float64(self.galaxy.shear.magnitude),
			np.float64(self.galaxy.shear.angle.value),
			np.float64(self.galaxy.velocityDispersion.value),
			np.float64(self.galaxy.angDiamDist.value),
			np.float64(self.quasar.angDiamDist.value),
			np.float64(self.__dLS.value),
			np.int32(width),
			np.int32(height),
			np.float64(self.configs.dTheta),
			np.float64(self.galaxy.position.to('rad').x),
			np.float64(self.galaxy.position.y),
			result_buffer_x,
			result_buffer_y)

		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x)
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y)
		print("Time Ray-Tracing = " + str(time.clock()-begin))
		return (result_nparray_x,result_nparray_y)

	cpdef configureMicrolensing(self):
		self.updateConfigs(displayGalaxy = False, displayQuasar = False)
		# self.updateGalaxy(center = )

	cpdef reconfigure(self):
		if self.__needsReconfiguring:
			# if self.__configs.isMicrolensing:
			# 	self.configureMicrolensing()
			begin = time.clock()
			self.__preCalculating = True
			self.__tree = WrappedTree()
			finalData = self.ray_trace(use_GPU = True)
			self.__tree.setDataFromNumpies(finalData)
			print("Time calculating = " + str(time.clock() - begin) + " seconds.")
			self.__preCalculating = False
			self.__needsReconfiguring = False


	def __calcER(self):
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))

	def calTheta(self):
		k = (4*math.pi*(const.c**-2).to('s2/km2').value * self.__dLS.value/self.quasar.angDiamDist.value* self.__galaxy.velocityDispersion.value * self.__galaxy.velocityDispersion.value)+self.quasar.position.magnitude()
		theta = (k/(1-(self.__dLS.value/self.quasar.angDiamDist.value)*self.galaxy.shearMag))
		theta2 = (k/(1+(self.__dLS.value/self.quasar.angDiamDist.value)*self.galaxy.shearMag))
		img1 = (self.quasar.position.magnitude() + math.sqrt(self.quasar.position.magnitude()**2 + 4 *theta**2))/2
		img2 = (self.quasar.position.magnitude() - math.sqrt(self.quasar.position.magnitude()**2 + 4 *theta**2))/2
		img3 = (self.quasar.position.magnitude() + math.sqrt(self.quasar.position.magnitude()**2 + 4 *theta2**2))/2
		img4 = (self.quasar.position.magnitude() - math.sqrt(self.quasar.position.magnitude()**2 + 4 *theta2**2))/2
		print(img1)
		print(img2)
		print(img3)
		print(img4)
		print("new")
		return (img1,img2,img3,img4)

	cpdef getMagnification(self):
		cdef a = np.float64 (self.__trueLuminosity)
		cdef b = np.float64 (self.__tree.query_point_count(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius.value))
		return b/a

	cpdef getFrame(self):
		if self.__needsReconfiguring:
			self.reconfigure()
		cdef int width = self.__configs.canvasDim
		cdef int height = self.__configs.canvasDim
		cdef np.float64_t dt = self.__configs.dt
		self.__quasar.setTime(self.time)
		ret = self.__tree.query_point(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius.value)
		self.img.fill(0)
		if self.configs.displayQuasar:
			self.quasar.draw(self.img,self.configs)
		if self.configs.displayStars:
			imgs = self.calTheta()
			self.galaxy.draw(self.img,self.configs, self.configs.displayGalaxy)
			# self.drawEinsteinRadius(self.img,self.einsteinRadius)
			# self.drawEinsteinRadius(self.img,self.calTheta()[0],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			# self.drawEinsteinRadius(self.img,self.calTheta()[1],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			# self.drawEinsteinRadius(self.img,self.calTheta()[2],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			self.drawEinsteinRadius(self.img,imgs[0],400,400)			# self.drawEinsteinRadius(self.img,self.calTheta()[0],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			self.drawEinsteinRadius(self.img,imgs[1],400,400)			# self.drawEinsteinRadius(self.img,self.calTheta()[0],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			self.drawEinsteinRadius(self.img,imgs[2],400,400)			# self.drawEinsteinRadius(self.img,self.calTheta()[0],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			self.drawEinsteinRadius(self.img,imgs[3],400,400)			# self.drawEinsteinRadius(self.img,self.calTheta()[0],400 + self.quasar.position.x/self.configs.dTheta,400 + self.quasar.position.y/self.configs.dTheta)
			# self.drawEinsteinRadius(self.img,self.einsteinRadius*(1-self.galaxy.shearMag/2))
		for pixel in ret:
			self.img.setPixel(pixel[0],pixel[1],1)
		return self.img

	def updateQuasar(self, redshift = None, radius = None, position = None, velocity = None, auto_configure = False):
		"""Resets parameters for the quasar inside the engine. Also recalculates any attributes dependent
		on the qusar's parameters. By default, does not re-ray trace the system. In order to ray trace, 
		set the kwarg auto_reconfigure = True."""
		if redshift != None and self.__quasar.redshift != redshift:
			self.__quasar.update(redshift = redshift)
			self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift)
			self.__calcER()
			self.__needsReconfiguring = True
		if radius != None and self.__quasar.radius != radius:
			self.__quasar.update(radius = radius)
		if position != None and self.__quasar.position != position:
			self.__quasar.update(position = position)
		if velocity != None and self.__quasar.velocity != velocity:
			self.__quasar.update(velocity = velocity)
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateGalaxy(self, redshift = None, velocityDispersion = None, shearMag = None, shearAngle = None, center = None, numStars = None, auto_configure = False):
		if redshift != None and self.__galaxy.redshift != redshift:
			self.__galaxy.update(redshift = redshift)
			self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift)
			self.__calcER()
			self.__needsReconfiguring = True
		if velocityDispersion != None and self.__galaxy.velocityDispersion != velocityDispersion:
			self.__galaxy.update(velocityDispersion = velocityDispersion)
			self.__calcER()
			self.__needsReconfiguring = True
		if shearMag != None and shearMag != self.__galaxy.shearMag:
			self.__galaxy.update(shearMag = shearMag)
			self.__needsReconfiguring = True
		if shearAngle != None and self.__galaxy.shearAngle != shearAngle:
			self.__galaxy.update(shearAngle = shearAngle)
			self.__needsReconfiguring = True
		if numStars != None and self.__galaxy.numStars != numStars:
			self.__galaxy.update(numStars = numStars)
			self.__galaxy.generateStars(self.configs)
			self.__needsReconfiguring = True
		if center != None and self.__galaxy.position != center:
			self.__galaxy.update(center = center)
			self.__needsReconfiguring = True
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateConfigs(self, dt = None, dTheta = None, canvasDim = None, frameRate = None, displayGalaxy = None, displayQuasar = None, displayStars = None, auto_configure = False):
		if dt != None and self.__configs.dt != dt:
			self.__configs.dt = dt
		if dTheta != None and self.__configs.dTheta != dTheta:
			self.__configs.dTheta = dTheta
			self.__trueLuminosity = math.pi * (self.quasar.radius.value/self.__configs.dTheta)**2
			self.__needsReconfiguring = True
		if canvasDim != None and self.__configs.canvasDim != canvasDim:
			self.__configs.canvasDim = canvasDim
			self.img = QtGui.QImage(self.__configs.canvasDim,self.__configs.canvasDim, QtGui.QImage.Format_Indexed8)
			self.img.setColorTable(self.__imgColors)
			self.img.fill(0)
			self.__needsReconfiguring = True
		if displayGalaxy != None:
			self.__configs.displayGalaxy = displayGalaxy
		if displayQuasar != None:
			self.__configs.displayQuasar = displayQuasar
		if displayStars != None:
			self.__configs.displayStars = displayStars
		if frameRate != None and self.__configs.frameRate != frameRate:
			self.__configs.frameRate = frameRate
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()





