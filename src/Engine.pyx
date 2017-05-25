# distutils: language=c++
# cython: profile=True
from __future__ import division
import numpy as np
cimport numpy as np
from Utility import WrappedTree
from Stellar import Galaxy
from Stellar import Quasar
from astropy.cosmology import WMAP7 as cosmo
from Utility import Vector2D
from Utility import zeroVector
import time
from astropy import constants as const
from astropy import units as u
import math
import pyopencl as cl
import pyopencl.tools
import os
from libcpp.vector cimport vector
import random
from PyQt5 import QtGui, QtCore
import cython
import ctypes
from libc.math cimport sin, cos, atan2, sqrt
from Parameters import Parameters
from scipy import interpolate
from libcpp.pair cimport pair
from libcpp cimport bool

cdef class Engine:

	def __init__(self, parameter=Parameters()):
		self.__parameters = parameter
		self.__preCalculating = False
		self.__trueLuminosity = math.pi * (self.__parameters.quasar.radius.value / self.__parameters.dTheta.value) ** 2

	@property
	def parameters(self):
		return self.__parameters

	def ray_trace(self, use_GPU=False):
		return self.ray_trace_gpu(False)


	cdef ray_trace_gpu(self, use_GPU):
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		os.environ['PYOPENCL_CTX'] = '2'
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray result_nparray_x = np.zeros((width, height), dtype=np.float64)
		cdef np.ndarray result_nparray_y = np.zeros((width, height), dtype=np.float64)
		cdef double dS = self.__parameters.quasar.angDiamDist.value
		cdef double dL = self.__parameters.galaxy.angDiamDist.value
		cdef double dLS = self.__parameters.dLS.value
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__parameters.galaxy.starArray

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

		# create buffers to send to device
		mf = cl.mem_flags		
		# input buffers
		stars_buffer_mass = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=stars_nparray_mass)
		stars_buffer_x = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=stars_nparray_x)
		stars_buffer_y = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=stars_nparray_y)
		# output buffers
		result_buffer_x = cl.Buffer(context, mf.READ_WRITE, result_nparray_x.nbytes)
		result_buffer_y = cl.Buffer(context, mf.READ_WRITE, result_nparray_y.nbytes)

		prg = cl.Program(context, open('Calculator/ray_tracer.cl').read()).build()
		prg.ray_trace(queue, (width, height), None,
			stars_buffer_mass,
			stars_buffer_x,
			stars_buffer_y,
			np.int32(len(stars_nparray_x)),
			np.float64((4 * const.G / (const.c * const.c)).to("lyr/solMass").value * dLS/dS/dL),
			np.float64(4 * math.pi * self.__parameters.galaxy.velocityDispersion**2 *(const.c ** -2).to('s2/km2').value*dLS/dS),
			np.float64(self.__parameters.galaxy.shear.magnitude),
			np.float64(self.__parameters.galaxy.shear.angle.value),
			np.int32(width),
			np.int32(height),
			np.float64(self.__parameters.dTheta.to('rad').value),
			np.float64(self.__parameters.galaxy.position.to('rad').x),
			np.float64(self.__parameters.galaxy.position.to('rad').y),
			result_buffer_x,
			result_buffer_y)


		cl.enqueue_copy(queue, result_nparray_x, result_buffer_x)
		cl.enqueue_copy(queue, result_nparray_y, result_buffer_y)
		print("Time Ray-Tracing = " + str(time.clock() - begin))
		return (result_nparray_x, result_nparray_y)


	def calTheta(self):
		k = (4 * math.pi * (const.c ** -2).to('s2/km2').value * self.__parameters.dLS.value / self.__parameters.quasar.angDiamDist.value * self.__parameters.galaxy.velocityDispersion.value * self.__parameters.galaxy.velocityDispersion.value) + (self.__parameters.quasar.position - self.__parameters.galaxy.position).magnitude()
		theta = (k / (1 - (self.__parameters.dLS.value / self.__parameters.quasar.angDiamDist.value) * self.__parameters.galaxy.shearMag))
		theta2 = (k / (1 + (self.__parameters.dLS.value / self.__parameters.quasar.angDiamDist.value) * self.__parameters.galaxy.shearMag))
		return (theta, theta2)

	@property
	def data(self):
		return self.__data

	cpdef getMagnification(self):
		cdef a = np.float64 (self.__trueLuminosity)
		cdef b = np.float64 (self.__tree.query_point_count(self.__parameters.quasar.observedPosition.x, self.__parameters.quasar.observedPosition.y, self.__parameters.quasar.radius.value))
		return b / a

	def reconfigure(self):
		pass
		
	cdef cythonMakeLightCurve(self, mmin, mmax, resolution, progressBar, smoothing): #Needs updateing
		if not self.__tree:
			self.reconfigure()
		begin = time.clock()
		if progressBar:
			progressBar.setMinimum(0)
			progressBar.setMaximum(int(resolution))
		cdef int counter = 0
		stepX = (mmax.x - mmin.x) / resolution
		stepY = (mmax.y - mmin.y) / resolution
		yAxis = np.ones(resolution)
		xVals = np.arange(0, 1, 1 / resolution)
		cdef int i = 0
		cdef double radius = self.__parameters.quasar.radius.value
		cdef double x = mmin.x
		cdef double y = mmin.y
		cdef double gx = self.__parameters.galaxy.position.x # Incorrect interfaced
		cdef double gy = self.__parameters.galaxy.position.y # Incorrect interfaced
		for i in range(0, resolution):
			x += stepX
			y += stepY
			yAxis[i] = self.__tree.query_point_count(x + gx, y + gy, radius) #Incorrect interfrace
			counter += 1
			if progressBar:
				progressBar.setValue(counter)
		print("clocked at = " + str(time.clock() - begin) + " seconds")
		if smoothing:
			xNew = np.arange(0, 1, 1 / (resolution * 10))
			yNew = np.empty_like(xNew)
			tck = interpolate.splrep(xVals, yAxis, s=0)
			yNew = interpolate.splev(xNew, tck, der=0)
			return (xNew, yNew)
		else:
			return (xVals, yAxis)

	cpdef visualize(self):
		cdef np.ndarray[np.float64_t, ndim=2] x
		cdef np.ndarray[np.float64_t, ndim=2] y
		x,y = self.ray_trace(use_GPU=True)
		cdef double xm = abs(x.min())
		cdef double ym = abs(y.min())
		x = (x + xm)
		y = (y + ym)
		extrema  = [abs(x.min()),abs(y.min()),abs(x.max()),abs(y.max())]
		cdef double extreme = max(extrema)
		x = x*(x.shape[0]-1)/extreme
		y = y*(y.shape[0]-1)/extreme
		cdef np.ndarray[np.int32_t, ndim=2] img = np.zeros_like(x, dtype=np.int32)
		cdef int endX = x.shape[0]
		cdef int endY = x.shape[1]
		cdef int i,j
		for i in range(0,endX):
			for j in range(0,endY):
				# for k in range(0,3):
				# 	for l in range(0,3):
				# 		img[<int> x[i-k,j-l],<int> y[i-k,j-l]] += 1
				img[<int> x[i,j],<int> y[i,j]] += 1
		return img

	def makeLightCurve(self, mmin, mmax, resolution=200, canvas=None, progressBar=None, smoothing=True):
		return self.cythonMakeLightCurve(mmin, mmax, resolution, progressBar, smoothing)


	def updateParameters(self, parameters):
		if self.__parameters is None:
			self.__parameters = parameters
			if self.__parameters.galaxy.percentStars > 0:
				self.__parameters.generateStars()
			self.reconfigure()
		elif not self.__parameters.isSimilar(parameters):
			self.__parameters = parameters
			if self.__parameters.galaxy.percentStars > 0:
				self.__parameters.generateStars()
			self.reconfigure()
		else:
			parameters.setStars(self.__parameters.stars)
			self.__parameters = parameters