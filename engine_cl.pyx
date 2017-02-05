# distutils: language=c++
# cython: profile=True

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
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2')) * (self.galaxy.shear.magnitude+1)#*206264806247.09637
		self.__galaxy.generateStars(self.einsteinRadius)
		# self.__trueLuminosity = math.pi * (self.__quasar.radius.value/self.__configs.dTheta)**2
		self.img = QtGui.QImage(self.__configs.canvasDim.x,self.__configs.canvasDim.y, QtGui.QImage.Format_Indexed8)
		self.img.setColorTable([QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255)])
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
		return self.ray_trace_gpu(use_GPU)

	def setShift(self,newConfigs,enabled, theta = math.pi):
		newConfigs.setShift(enabled,self.einsteinRadius, theta = math.pi)
		if enabled:
			self.__galaxy.generateStars
			newConfigs.displayQuasar = False
			newConfigs.displayGalaxy = False
		##### TODO #####


	cdef ray_trace_gpu(self,use_GPU):
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		if use_GPU:
			os.environ['PYOPENCL_CTX'] = '0:1'
		else:
			os.environ['PYOPENCL_CTX'] = '0:0'
		cdef int height = self.__configs.canvasDim.y
		cdef int width = self.__configs.canvasDim.x
		cdef double dTheta = self.__configs.dTheta
		cdef np.ndarray result_nparray_x = np.ndarray((width,height), dtype = np.float32)
		cdef np.ndarray result_nparray_y = np.ndarray((width,height), dtype = np.float32)
		stars_nparray = self.__galaxy.getStarArray()

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

		# create buffers to send to device
		mf = cl.mem_flags
		dtype = stars_nparray.dtype

		dtype, c_decl = cl.tools.match_dtype_to_c_struct(context.devices[0],'lenser_struct',dtype)
		cl.tools.get_or_register_dtype('lenser_struct',stars_nparray.dtype)

		#input buffers
		stars_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray)

		#output buffers
		result_buffer_x = cl.Buffer(context, mf.READ_WRITE, result_nparray_x.nbytes)
		result_buffer_y = cl.Buffer(context, mf.READ_WRITE, result_nparray_y.nbytes)

		# read and compile opencl kernel
		prg = cl.Program(context,c_decl + open('engine_helper.cl').read()).build(['-cl-fp32-correctly-rounded-divide-sqrt'])
		prg.ray_trace(queue,(width,height),None,
			stars_buffer,
			np.int32(len(stars_nparray)),
			np.float32((4*const.G/(const.c*const.c)).to("lyr/solMass").value), #np.float32(0.12881055652653947), #
			np.float32(4*math.pi*(const.c**-2).to('s2/km2').value),#np.float32(28.83988945290979), #
			np.float32(math.sin(2*self.galaxy.shear.angle.value+math.pi/2)),
			np.float32(-math.cos(2*self.galaxy.shear.angle.value+math.pi/2)),
			np.float32(self.galaxy.velocityDispersion),
			np.float32(self.galaxy.angDiamDist.value),
			np.float32(self.quasar.angDiamDist.value),
			np.float32(self.__dLS.value),
			np.int32(width),
			np.int32(height),
			np.float32(self.configs.dTheta),
			np.float32(self.configs.frameShift.x),
			np.float32(self.configs.frameShift.y),
			result_buffer_x,
			result_buffer_y)

		# clean up GPU memory while copying data back into RAM
		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x)
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y)

		print(begin-time.clock())
		return (result_nparray_x,result_nparray_y)

	# @cython.boundscheck(False) # turn off bounds-checking for entire function
	# @cython.wraparound(False)  # turn off negative index wrapping for entire function
	# cdef ray_trace_gpu(self,use_GPU):
	# 	cdef int height = self.__configs.canvasDim.y
	# 	cdef int width = self.__configs.canvasDim.x
	# 	cdef double dTheta = self.__configs.dTheta
	# 	cdef np.ndarray[dtype=np.float64_t, ndim=2] result_nparray_x = np.ndarray((width,height), dtype = np.float32)
	# 	cdef np.ndarray[dtype=np.float64_t, ndim=2] result_nparray_y = np.ndarray((width,height), dtype = np.float32)
	# 	cdef np.ndarray[dtype=lenser_struct, ndim=1] stars_nparray = self.__galaxy.getStarArray()
	# 	engineHelper.ray_trace(&stars_nparray[0],#stars_nparray.ctypes.data_as(ctypes.c_void_p),
	# 		np.int32(self.__galaxy.numStars),
	# 		np.float32((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
	# 		np.float32(4*math.pi*(const.c**-2).to('s2/km2').value),
	# 		np.float32(self.galaxy.angDiamDist.value),
	# 		np.float32(self.quasar.angDiamDist.value),
	# 		np.float32(self.__dLS.value),
	# 		np.int32(width),
	# 		np.int32(height),
	# 		np.float32(self.configs.dTheta),
	# 		np.float32(self.configs.frameShift.x),
	# 		np.float32(self.configs.frameShift.y),
	# 		&result_nparray_x[0,0],
	# 		&result_nparray_y[0,0])

	cpdef reconfigure(self):
		if self.__needsReconfiguring:
			begin = time.clock()
			self.__preCalculating = True
			self.__tree = WrappedTree()
			finalData = self.ray_trace(use_GPU = True)
			self.__tree.setDataFromNumpies(finalData)
			print("Time calculating = " + str(time.clock() - begin) + " seconds.")
			self.__preCalculating = False
			self.__needsReconfiguring = False


	cpdef getMagnification(self):
		cdef a = np.float32(self.__trueLuminosity)
		cdef b = np.float32(self.__tree.query_point_count(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius.value))
		return b/a

	cdef buildTree(self, data):
		xvals = data[0]
		yvals = data[1]
		cdef int width = self.__configs.canvasDim.x
		cdef int height = self.__configs.canvasDim.y
		cdef double __dS = self.quasar.angDiamDist.value
		cdef int i = 0
		cdef int j = 0
		for i in range(width):
			for j in range(height):
				self.__tree.insert(i,j,xvals[i,j],yvals[i,j])
		

	cpdef getFrame(self):
		print("New Frame")
		if self.__needsReconfiguring:
			self.reconfigure()
		cdef int width = self.__configs.canvasDim.x
		cdef int height = self.__configs.canvasDim.y
		cdef double dt = self.__configs.dt
		self.__quasar.setTime(self.time)
		ret = self.__tree.query_point(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius.value)
		self.img.fill(0)
		if self.configs.displayQuasar:
			self.quasar.draw(self.img,self.configs)
		if self.configs.displayGalaxy:
			self.galaxy.draw(self.img,self.configs)
		for pixel in ret:
			self.img.setPixel(pixel[0],pixel[1],1)
		return self.img

		

	cdef calcDeflections(self):
		pass


	cdef queryTree(self,position):
		pass


	def updateQuasar(self,quasar = None,redshift = None,position = None,radius = None,velocity = None, auto_configure = True):
		newQ = quasar or self.__quasar
		newQ.update(redshift = redshift,position = position,radius = radius,velocity = velocity)
		if self.quasar.redshift != newQ.redshift:
			self.__needsReconfiguring = True
			self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,newQ.redshift).to('lyr')
			self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2')) * (self.galaxy.shear.magnitude+1)#*206264806247.09637
		# self.__trueLuminosity = math.pi * (newQ.radius.value/self.__configs.dTheta)**2
		self.__quasar = newQ
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateGalaxy(self,galaxy = None ,redshift = None, velocityDispersion = None, radius = None, numStars = None, auto_configure = True):
		if galaxy != None:
			if galaxy.redshift != self.galaxy.redshift or galaxy.velocityDispersion != self.galaxy.velocityDispersion or galaxy.numStars != self.galaxy.numStars or galaxy.shear.magnitude != self.galaxy.shear.magnitude or galaxy.shear.angle != self.galaxy.shear.angle:
				self.__needsReconfiguring = True
		if galaxy is None:
			self.__needsReconfiguring = True
		self.__galaxy = galaxy or self.__galaxy
		self.__galaxy.update(redshift = redshift,velocityDispersion = velocityDispersion,numStars = numStars)
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2')) * (self.galaxy.shear.magnitude+1)#*206264806247.09637
		self.__galaxy.generateStars(self.einsteinRadius)
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateConfigs(self,configs = None, dt = None, dTheta = None, canvasDim = None, auto_configure = True, frameRate = None, displayGalaxy = None, displayQuasar = None,colorQuasar = None, shiftGalacticCenter = None):
		#Need to redo this so that upon rescaling, centers around screeen
		newConfigs = configs or self.__configs
		newConfigs.dt = dt or newConfigs.dt
		newConfigs.dTheta = dTheta or newConfigs.dTheta
		newConfigs.canvasDim = canvasDim or newConfigs.canvasDim
		if colorQuasar is not None:
			newConfigs.colorQuasar = colorQuasar
		if shiftGalacticCenter is not None:
			newConfigs.shiftGalaxy = shiftGalacticCenter
		if displayGalaxy is not None:
			newConfigs.displayGalaxy = displayGalaxy
		if displayQuasar is not None:
			newConfigs.displayQuasar = displayQuasar
		if newConfigs.dTheta - self.__configs.dTheta != 0:
			# self.__trueLuminosity = math.pi * (self.quasar.radius.value/newConfigs.dTheta)**2
			self.__needsReconfiguring = True
		if newConfigs.canvasDim - self.__configs.canvasDim != zeroVector:
			##### ERROR HERE causing it to continually recalculate #####
			# self.__needsReconfiguring = True
			self.img = QtGui.QImage(self.__configs.canvasDim.x,self.__configs.canvasDim.y, QtGui.QImage.Format_Indexed8)
			self.img.setColorTable([QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255)])
			self.img.fill(0)
		if shiftGalacticCenter is not None:
			if shiftGalacticCenter:
				self.__needsReconfiguring = True
				self.setShift(newConfigs,shiftGalacticCenter, theta = math.pi)
				newConfigs.dTheta = 100  #Need to fix
				# self.__trueLuminosity = math.pi * (self.quasar.radius.value/newConfigs.dTheta)**2
			else:
				self.__needsReconfiguring = True
		self.__configs = newConfigs
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()


