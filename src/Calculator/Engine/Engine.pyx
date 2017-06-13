# distutils: language=c++
# cython: profile=True
from __future__ import division

import ctypes
import os
import random
import time
import math

from PyQt5 import QtGui, QtCore
from astropy import constants as const
from astropy import units as u
from astropy.cosmology import WMAP7 as cosmo
import cython
from cython.parallel import prange
import pyopencl.tools
from scipy import interpolate

from Utility import Vector2D
from Utility import zeroVector
import numpy as np
import pyopencl as cl


cimport numpy as np
from libcpp.vector cimport vector
from libc cimport math as CMATH
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
		return self.ray_trace_gpu()

	cdef ray_trace_gpu(self):
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		os.environ['PYOPENCL_CTX'] = '2'
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray result_nparray_x = np.zeros((width, height), dtype=np.float64)
		cdef np.ndarray result_nparray_y = np.zeros((width, height), dtype=np.float64)
# 		cdef double* lol = <double*> result_nparray_x.data/
		cdef double dS = self.__parameters.quasar.angDiamDist.value
		cdef double dL = self.__parameters.galaxy.angDiamDist.value
		cdef double dLS = self.__parameters.dLS.value
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__parameters.galaxy.starArray
# 		print(len(stars_nparray_mass))
		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)
		# create buffers to send to device
		mf = cl.mem_flags		
		# input buffers
		stars_buffer_mass = np.float64(0.0)
		stars_buffer_x = np.float64(0.0)
		stars_buffer_y = np.float64(0.0)
		if len(stars_nparray_mass) > 0:
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
		del(result_buffer_x)
		del(result_buffer_y)
# 		print("Time Ray-Tracing = " + str(time.clock() - begin))
		return (result_nparray_x, result_nparray_y)


	@cython.boundscheck(False)
	@cython.wraparound(False)
	cdef ray_trace_cpu(self):
		begin = time.clock()
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray[np.float64_t,ndim = 2] result_nparray_x = np.zeros((width, height), dtype=np.float64)
		cdef np.ndarray[np.float64_t,ndim = 2] result_nparray_y = np.zeros((width, height), dtype=np.float64)
		cdef double dS = self.__parameters.quasar.angDiamDist.value
		cdef double dL = self.__parameters.galaxy.angDiamDist.value
		cdef double dLS = self.__parameters.dLS.value
		cdef np.ndarray[np.float64_t,ndim = 1] stars_mass, stars_x, stars_y
		stars_mass, stars_x, stars_y = self.__parameters.galaxy.starArray
		cdef double shearMag = self.__parameters.galaxy.shear.magnitude
		cdef double shearAngle = self.__parameters.galaxy.shear.angle.value
		cdef double centerX = self.__parameters.galaxy.position.to('rad').x
		cdef double centerY = self.__parameters.galaxy.position.to('rad').y
		cdef double sis_constant = 	np.float64(4 * math.pi * self.__parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
		cdef double point_constant = (4 * const.G / (const.c * const.c)).to("lyr/solMass").value * dLS / dS / dL
		cdef int numStars = len(stars_x)
		cdef double pi2 = math.pi/2
		cdef int x, y, i
		cdef double incident_angle_x, incident_angle_y, r, deltaR_x, deltaR_y, phi
		for x in prange(0,width,1,nogil=True,schedule='static',chunksize=int(width/4),num_threads=4):
			for y in range(0,height):
				incident_angle_x = (x - width/2)*dTheta
				incident_angle_y = (y-height/2)*dTheta
				
				#SIS
				deltaR_x = incident_angle_x - centerX
				deltaR_y = incident_angle_y - centerY
				r = sqrt(deltaR_x*deltaR_x+deltaR_y*deltaR_y)
				if r == 0.0:
					result_nparray_x[x,y] += deltaR_x 
					result_nparray_y[x,y] += deltaR_y
				else:
					result_nparray_x[x,y] += deltaR_x*sis_constant/r 
					result_nparray_y[x,y] += deltaR_y*sis_constant/r 
				
				#Shear
				phi = 2*(shearAngle+pi2)-CMATH.atan2(deltaR_y,deltaR_x)
				result_nparray_x[x,y] += shearMag*r*CMATH.cos(phi)
				result_nparray_y[x,y] += shearMag*r*CMATH.sin(phi)
				result_nparray_x[x,y] = deltaR_x - result_nparray_x[x,y]
				result_nparray_y[x,y] = deltaR_y - result_nparray_y[x,y]	
		print("Time Ray-Tracing = " + str(time.clock() - begin))			
		return (result_nparray_x,result_nparray_y)
	

		
	
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
			b = np.float64 (self.query_data_length(self.__parameters.quasar.observedPosition.x, self.__parameters.quasar.observedPosition.y, self.__parameters.quasar.radius.value))
			return b / self.trueLuminosity

	def reconfigure(self):
		"""
		Virtual method to be implemented by subclasses. Provides an interface for configuring the engine by calculating and storing ray-tracing data.
		Automatically called upon calling update parameters, when a new set of parameters warranting a recalculation of the system is passed in."""
		pass
	
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil:
		return 0
		
	cpdef makeLightCurve(self, object mmin, object mmax, int resolution):  # Needs updateing
		"""Deprecated"""
		print("MAKING LIGHT CURVE")
		while self.__preCalculating:
			print("Waiting")
			time.sleep(0.1)
		mmax = mmax.to('rad')
		mmin = mmin.to('rad')
		cdef double stepX = (mmax.x - mmin.x) / resolution
		cdef double stepY = (mmax.y - mmin.y) / resolution
		cdef np.ndarray[np.float64_t, ndim=1] yAxis = np.ones(resolution)
# 		cdef np.ndarray[np.float64_t, ndim=2] xVals = np.ndarray((resolution,2))
		cdef int i = 0
		cdef double radius = self.__parameters.queryQuasarRadius
		cdef double x = mmin.x
		cdef double y = mmin.y
		cdef bool hasVel = self.__parameters.galaxy.hasStarVel
		cdef double trueLuminosity = self.trueLuminosity
		cdef int aptLuminosity = 0
		with nogil:
			for i in range(0, resolution):
				x += stepX
				y += stepY
# 				xVals[i,0] = x
# 				xVals[i,1] = y
				aptLuminosity = self.query_data_length(x, y, radius)  # Incorrect interface
				yAxis[i] = (<double> aptLuminosity)/trueLuminosity
				if hasVel:
					with gil:
						self.__parameters.galaxy.moveStars(self.__parameters.dt)
						self.reconfigure()
# 		return (xVals, yAxis)
		return yAxis
	
	cpdef makeMagMap(self, object topLeft, double height, double width, int resolution): #######Possibly slow implementation. Temporary
		########################## I STILL WANT TO SEE IF CAN MAKE MAGMAP FROM THE SOURCEPLANE RAY TRACE LOCATIONS, BUT IN THE MEANTIME
		########################## I'M DOING IT THE OLD-FASHIONED WAY #################################################################
		cdef double stepDown = height/resolution
		retArr = np.ndarray((resolution,resolution), dtype=np.float64)
		cdef int i = 0
		for i in range(0,resolution):
			s = topLeft - Vector2D(0,stepDown*i)
			f = topLeft + Vector2D(width,-stepDown*i)
			retArr[i] = self.makeLightCurve(s,f,resolution)
		return retArr
		

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
				stars = self.__parameters.generateStars()
				parameters.setStars(stars)
			self.reconfigure()
		elif not self.__parameters.isSimilar(parameters):
			self.__parameters = parameters
			if self.__parameters.galaxy.percentStars > 0:
				stars = self.__parameters.generateStars()
				parameters.setStars(stars)
			self.reconfigure()
		else:
			parameters.setStars(self.__parameters.stars)
			self.__parameters = parameters
