# distutils: language=c++
# cython: profile=True
from __future__ import division

import ctypes
import math
import os
import random
import time

from PyQt5 import QtGui, QtCore
from astropy import constants as const
from astropy import units as u
from astropy.cosmology import WMAP7 as cosmo
import cython
import pyopencl.tools
from scipy import interpolate

from Utility import Vector2D
from Utility import zeroVector
import numpy as np
import pyopencl as cl


cimport numpy as np
from libcpp.vector cimport vector
from libc.math cimport sin, cos, atan2, sqrt
from libcpp.pair cimport pair
from libcpp cimport bool

cdef class Engine:
	"""
		Abstract class for storing and calculating an arbitrarily complex lensing system.

		Contains heavily optimized code, written in cython and utilizing OpenCL for further optimization by performing calculations on the 
		graphics processing unit when hardware permits.
	"""

	def __init__(self, parameter=None):
		self.__parameters = parameter
		self.__preCalculating = False

	@property
	def parameters(self):
		return self.__parameters

	def ray_trace(self, use_GPU=False):
		"""Python-callable wrapper for ray_trace_gpu.
			Reverse-ray-traces possible paths a photon could take from the observer to source plane.
			Returns a tuple of numpy arrays, the first of which contains the x and y-coordinates of each path's intersection with
			the source plane, respectively.

			Performs calculations with OpenCL acceleration. If the computer's graphics processor supports 64-bit floating-point arithmetic,
			the graphics processor may be used. Otherwise, will perform calculations on the CPU."""
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
			np.float64((4 * const.G / (const.c * const.c)).to("lyr/solMass").value * dLS / dS / dL),
			np.float64(4 * math.pi * self.__parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS),
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
		"""
		Read-only access to the spatial data structure used to store pixel locations where they intersect the source plane."""
		return self.__data

	@property
	def trueLuminosity(self):
		return math.pi * (self.parameters.quasar.radius.value / self.parameters.dTheta.value) ** 2


	cpdef getMagnification(self, pixelCount):
		"""
		Returns the magnification coefficient of the quasar seen by the observer, after lensing effects have been accounted for."""
		if pixelCount:
			return pixelCount / self.trueLuminosity
		else:
			b = np.float64 (self.__tree.query_point_count(self.__parameters.quasar.observedPosition.x, self.__parameters.quasar.observedPosition.y, self.__parameters.quasar.radius.value))
			return b / self.trueLuminosity

	def reconfigure(self):
		"""
		Virtual method to be implemented by subclasses. Provides an interface for configuring the engine by calculating and storing ray-tracing data.
		Automatically called upon calling update parameters, when a new set of parameters warranting a recalculation of the system is passed in."""
		pass
	
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil:
		return 0
		
	cdef makeLightCurve(self, object mmin, object mmax, int resolution):  # Needs updateing
		"""Deprecated"""
		cdef double stepX = (mmax.x - mmin.x) / resolution
		cdef double stepY = (mmax.y - mmin.y) / resolution
		cdef np.ndarray[np.float64_t, ndim=1] yAxis = np.ones(resolution)
		cdef np.ndarray[np.float64_t, ndim=2] xVals = np.ndarray((resolution,2))
		cdef int i = 0
		cdef double radius = self.__parameters.quasar.radius.value
		cdef double x = mmin.x
		cdef double y = mmin.y
		cdef double gx = self.__parameters.galaxy.position.x  # Incorrect interfaced
		cdef double gy = self.__parameters.galaxy.position.y  # Incorrect interfaced
		for i in range(0, resolution):
			x += stepX
			y += stepY
			xVals[i,0] = x
			xVals[i,1] = y
			yAxis[i] = self.query_data_length(x + gx, y + gy, radius)  # Incorrect interface
			if self.__parameters.galaxy.hasStarVel:
				self.__parameters.galaxy.moveStars(self.__parameters.dt)
				self.reconfigure()
		return (xVals, yAxis)

	cpdef visualize(self):
		"""
		Calcualtes and returns an image of the system's magnification map for a point source. 

		This calculation is performed by correlating the density of rays on the source plane to a magnification coefficient at that location."""
		cdef np.ndarray[np.float64_t, ndim = 2] x
		cdef np.ndarray[np.float64_t, ndim = 2] y
		x, y = self.ray_trace(use_GPU=True)
		cdef double xm = abs(x.min())
		cdef double ym = abs(y.min())
		x = (x + xm)
		y = (y + ym)
		extrema = [abs(x.min()), abs(y.min()), abs(x.max()), abs(y.max())]
		cdef double extreme = max(extrema)
		x = x * (x.shape[0] - 1) / extreme
		y = y * (y.shape[0] - 1) / extreme
		cdef np.ndarray[np.int32_t, ndim = 2] img = np.zeros_like(x, dtype=np.int32)
		cdef int endX = x.shape[0]
		cdef int endY = x.shape[1]
		cdef int i, j
		for i in range(0, endX):
			for j in range(0, endY):
				img[ < int > x[i, j], < int > y[i, j]] += 1
		return img



	def updateParameters(self, parameters):
		"""Provides an interface for updating the parameters describing the lensed system to be modeled.

		If the new system warrants a recalculation of spatial data, will call the function 'reconfigure' automatically"""
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
