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
import time
from astropy import constants as const
import math
import pyopencl as cl
import pyopencl.tools
import os
from SpatialTree cimport SpatialTree, Pixel
from libcpp.vector cimport vector
import random
from PyQt5 import QtGui


cdef class Engine_cl:

	def __init__(self,quasar,galaxy,configs, auto_configure = True):
		self.__quasar = quasar
		self.__galaxy = galaxy
		self.__configs = configs
		self.__preCalculating = False
		self.__needsReconfiguring = True
		self.time = 0.0
		self.__dL = self.__galaxy.angDiamDist #ADD
		self.__dS = self.__quasar.angDiamDist
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr').value
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.__dS /((const.c**2).to('km2/s2').value)
		self.__galaxy.generateStars(self.einsteinRadius)
		self.__trueLuminosity = math.pi * (self.__quasar.radius/self.__configs.dTheta)**2
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

	def ray_trace(self, use_GPU = True):
		return self.ray_trace_gpu(use_GPU)


	cdef ray_trace_gpu(self,use_GPU):
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
			np.int32(self.__galaxy.numStars),
			np.float32((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
			np.float32(4*math.pi*(const.c**-2).to('s2/km2').value),
			np.float32(self.__dL),
			np.float32(self.__dS),
			np.float32(self.__dLS),
			np.int32(width),
			np.int32(height),
			np.float32(self.__configs.dTheta),
			result_buffer_x,
			result_buffer_y)

		# clean up GPU memory while copying data back into RAM
		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x).wait()
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y).wait()

		return (result_nparray_x,result_nparray_y)



	cpdef reconfigure(self):
		if self.__needsReconfiguring:
			begin = time.clock()
			self.__preCalculating = True
			self.__tree = WrappedTree()
			finalData = self.ray_trace()
			self.__tree.setDataFromNumpies(finalData)
			print("Time calculating = " + str(time.clock() - begin) + " seconds.")
			self.__preCalculating = False
			self.__needsReconfiguring = False


	cpdef getMagnification(self):
		cdef a = np.double(self.__trueLuminosity)
		cdef b = np.double(self.__tree.query_point_count(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius))
		return b/a

	cdef buildTree(self, data):
		xvals = data[0]
		yvals = data[1]
		cdef int width = self.__configs.canvasDim.x
		cdef int height = self.__configs.canvasDim.y
		cdef double __dS = self.__dS
		cdef int i = 0
		cdef int j = 0
		for i in range(width):
			for j in range(height):
				self.__tree.insert(i,j,xvals[i,j],yvals[i,j])
		

	cpdef drawFrame(self):
		if self.__needsReconfiguring:
			self.reconfigure()
		cdef int width = self.__configs.canvasDim.x
		cdef int height = self.__configs.canvasDim.y
		cdef double dt = self.__configs.dt
		self.__quasar.setTime(self.time)
		ret = self.__tree.query_point(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius)
		self.img.fill(0)
		if self.configs.displayQuasar:
			self.quasar.draw(self.img,self.configs.dTheta)
		if self.configs.displayGalaxy:
			self.galaxy.draw(self.img,self.configs.dTheta)
		for pixel in ret:
			self.img.setPixel(pixel[0],pixel[1],1)
		return self.img

		

	cdef calcDeflections(self):
		pass


	cdef queryTree(self,position):
		pass


	def updateQuasar(self,quasar = None,redshift = None,position = None,radius = None,velocity = None, auto_configure = True):
		newQ = quasar or self.__quasar
		newQ.update(redshift,position,radius,velocity)
		if self.quasar.redshift != newQ.redshift:
			self.__needsReconfiguring = True
			self.__dS = newQ.angDiamDist
			self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,newQ.redshift).to('lyr').value
			self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.__dS /((const.c**2).to('km2/s2').value)
		self.__trueLuminosity = math.pi * (newQ.radius/self.__configs.dTheta)**2
		self.__quasar = newQ
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateGalaxy(self,galaxy = None ,redshift = None, velocityDispersion = None, radius = None, numStars = None, auto_configure = True):
		if galaxy != None:
			if galaxy.redshift != self.galaxy.redshift or galaxy.velocityDispersion != self.galaxy.velocityDispersion or galaxy.numStars != self.galaxy.numStars or galaxy.shear.strength != self.galaxy.shear.strength or galaxy.shear.angle != self.galaxy.shear.angle:
				self.__needsReconfiguring = True
		if galaxy is None:
			self.__needsReconfiguring = True
		self.__galaxy = galaxy or self.__galaxy
		self.__galaxy.update(redshift,velocityDispersion,radius,numStars)
		self.__dL = self.__galaxy.angDiamDist #ADD
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr').value
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.__dS /((const.c**2).to('km2/s2').value)
		self.__galaxy.generateStars(self.einsteinRadius)
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateConfigs(self,configs = None, dt = None, dTheta = None, canvasDim = None, auto_configure = True):
		newConfigs = configs or self.__configs
		newConfigs.dt = dt or self.__configs.dt
		newConfigs.dTheta = dTheta or self.__configs.dTheta
		newConfigs.canvasDim = canvasDim or self.__configs.canvasDim
		self.__configs = newConfigs
		if newConfigs.dTheta != self.__configs.dTheta:
			self.__trueLuminosity = math.pi * (self.quasar.radius/self.__configs.dTheta)**2
			self.__needsReconfiguring = True
		if newConfigs.canvasDim != self.__configs.canvasDim:
			self.__needsReconfiguring = True
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

