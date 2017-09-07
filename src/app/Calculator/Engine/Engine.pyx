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
from scipy import interpolate

from ...Utility import Vector2D
from ...Utility import zeroVector
from app.Preferences import GlobalPreferences
import numpy as np

from .. import gpu_kernel

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

	def __init__(self, parameters=None):
		self.__parameters = parameters
		self.__preCalculating = False
		self.core_count = GlobalPreferences['core_count']

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
		# try:
		# 	return self.ray_trace_gpu()
		# except:
		return self.ray_trace_gpu()

	cdef ray_trace_gpu(self):
		import pyopencl.tools
		import pyopencl as cl
		begin = time.clock()
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray result_nparray_x = np.zeros((width, height), dtype=np.float64)
		cdef np.ndarray result_nparray_y = np.zeros((width, height), dtype=np.float64)
		cdef double dS = self.__parameters.quasar.angDiamDist.to('lyr').value
		cdef double dL = self.__parameters.galaxy.angDiamDist.to('lyr').value
		cdef double dLS = self.__parameters.dLS.to('lyr').value
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__parameters.galaxy.starArray

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
		prg = cl.Program(context, open('app/Calculator/ray_tracer.cl').read()).build()
		prg.ray_trace(queue, (width, height), None,
			stars_buffer_mass,
			stars_buffer_x,
			stars_buffer_y,
			np.int32(len(stars_nparray_x)),
			np.float64((4 * const.G / const.c / const.c).to("lyr/solMass").value * dLS / dS / dL),
			np.float64(4 * math.pi * self.__parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS),
			np.float64(self.__parameters.galaxy.shear.magnitude),
			np.float64(self.__parameters.galaxy.shear.angle.to('rad').value),
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
		return (result_nparray_x, result_nparray_y)

	cdef ray_trace_gpu_raw(self):
		begin = time.clock()
		import pyopencl.tools
		import pyopencl as cl
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray result_nparray_x = np.zeros((width, height), dtype=np.float64)
		cdef np.ndarray result_nparray_y = np.zeros((width, height), dtype=np.float64)
		cdef double dS = self.__parameters.quasar.angDiamDist.to('lyr').value
		cdef double dL = self.__parameters.galaxy.angDiamDist.to('lyr').value
		cdef double dLS = self.__parameters.dLS.to('lyr').value
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__parameters.galaxy.starArray

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
		prg = cl.Program(context, gpu_kernel.read()).build()
		prg.ray_trace(queue, (width, height), None,
			stars_buffer_mass,
			stars_buffer_x,
			stars_buffer_y,
			np.int32(0),
			np.float64((4 * const.G / const.c / const.c).to("lyr/solMass").value * dLS / dS / dL),
			np.float64(4 * math.pi * self.__parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS),
			np.float64(self.__parameters.galaxy.shear.magnitude),
			np.float64(self.__parameters.galaxy.shear.angle.to('rad').value),
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
		return (result_nparray_x, result_nparray_y)

	@cython.boundscheck(False)
	@cython.wraparound(False)
	cdef ray_trace_cpu(self):
		begin = time.clock()
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		height = height//2
		width = width//2
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray[np.float64_t,ndim = 2] result_nparray_x = np.zeros((width*2, height*2), dtype=np.float64)
		cdef np.ndarray[np.float64_t,ndim = 2] result_nparray_y = np.zeros((width*2, height*2), dtype=np.float64)
		cdef double dS = self.__parameters.quasar.angDiamDist.to('lyr').value
		cdef double dL = self.__parameters.galaxy.angDiamDist.to('lyr').value
		cdef double dLS = self.__parameters.dLS.to('lyr').value
		cdef np.ndarray[np.float64_t,ndim = 1] stars_mass, stars_x, stars_y
		cdef int numStars = 0
		if self.__parameters.galaxy.percentStars > 0.0:
			stars_mass, stars_x, stars_y = self.__parameters.galaxy.starArray
			numStars = len(stars_x)
		cdef double shearMag = self.__parameters.galaxy.shear.magnitude
		cdef double shearAngle = self.__parameters.galaxy.shear.angle.value
		cdef double centerX = self.__parameters.galaxy.position.to('rad').x
		cdef double centerY = self.__parameters.galaxy.position.to('rad').y
		cdef double sis_constant = 	np.float64(4 * math.pi * self.__parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
		cdef double point_constant = (4 * const.G / const.c / const.c).to("lyr/solMass").value * dLS / dS / dL
		cdef double pi2 = math.pi/2
		cdef int x, y, i
		cdef double incident_angle_x, incident_angle_y, r, deltaR_x, deltaR_y, phi
		for x in prange(0,width*2,1,nogil=True,schedule='static',num_threads=self.core_count):
			for y in range(0,height*2):
				incident_angle_x = (x - width)*dTheta
				incident_angle_y = (height - y)*dTheta

				for i in range(numStars):
					deltaR_x = incident_angle_x - stars_x[i]
					deltaR_y = incident_angle_y - stars_y[i]
					r = deltaR_x*deltaR_x + deltaR_y*deltaR_y
					if r != 0.0:
						result_nparray_x[x,y] += deltaR_x*stars_mass[i]*point_constant/r;
						result_nparray_y[x,y] += deltaR_y*stars_mass[i]*point_constant/r;				
				
				#SIS
				deltaR_x = incident_angle_x - centerX
				deltaR_y = incident_angle_y - centerY
				r = sqrt(deltaR_x*deltaR_x+deltaR_y*deltaR_y)
				if r != 0.0:
					result_nparray_x[x,y] += deltaR_x*sis_constant/r 
					result_nparray_y[x,y] += deltaR_y*sis_constant/r

				#Shear
				phi = 2*(pi2 - shearAngle )-CMATH.atan2(deltaR_y,deltaR_x)
				result_nparray_x[x,y] += shearMag*r*CMATH.cos(phi)
				result_nparray_y[x,y] += shearMag*r*CMATH.sin(phi)
				result_nparray_x[x,y] = deltaR_x - result_nparray_x[x,y]
				result_nparray_y[x,y] = deltaR_y - result_nparray_y[x,y]	
		print("Time Ray-Tracing = " + str(time.clock() - begin))			
		return (result_nparray_x,result_nparray_y)
	

	def getCenterCoords(self,params = None):

		#Pulling parameters out of parameters class
		parameters = params or self.__parameters
		height = parameters.canvasDim
		width = parameters.canvasDim
		dTheta = parameters.dTheta.value
		dS = parameters.quasar.angDiamDist.value
		dL = parameters.galaxy.angDiamDist.value
		dLS = parameters.dLS.value
		shearMag = parameters.galaxy.shear.magnitude
		shearAngle = parameters.galaxy.shear.angle.value
		centerX = parameters.galaxy.position.to('rad').x
		centerY = parameters.galaxy.position.to('rad').y
		sis_constant = 	np.float64(4 * math.pi * parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
		point_constant = (4 * const.G / (const.c * const.c)).to("lyr/solMass").value * dLS / dS / dL
		pi2 = math.pi/2

		#Calculation variables
		resx = 0
		resy = 0

		#Calculation is Below
		incident_angle_x = 0.0
		incident_angle_y = 0.0
		
		try:
			#SIS
			deltaR_x = incident_angle_x - centerX
			deltaR_y = incident_angle_y - centerY
			r = sqrt(deltaR_x*deltaR_x+deltaR_y*deltaR_y)
			if r == 0.0:
				resx += deltaR_x 
				resy += deltaR_y
			else:
				resx += deltaR_x*sis_constant/r 
				resy += deltaR_y*sis_constant/r 
			
			#Shear
			phi = 2*(pi2 - shearAngle)-CMATH.atan2(deltaR_y,deltaR_x)
			resx += shearMag*r*CMATH.cos(phi)
			resy += shearMag*r*CMATH.sin(phi)
			resx = deltaR_x - resx
			resy = deltaR_y - resy
		except ZeroDivisionError:
			resx = 0.0
			resy = 0.0
		return Vector2D(resx,resy,'rad')

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
		
	cdef makeLightCurve_helper(self, object mmin, object mmax, int resolution):  # Needs updateing
		"""Deprecated"""
# 		print("MAKING LIGHT CURVE")
		while self.__preCalculating:
			print("Waiting")
			time.sleep(0.1)
		mmax = mmax.to('rad')
		mmin = mmin.to('rad')
		cdef double stepX = (mmax.x - mmin.x) / resolution
		cdef double stepY = (mmax.y - mmin.y) / resolution
		cdef np.ndarray[np.float64_t, ndim=1] yAxis = np.ones(resolution)
		cdef int i = 0
		cdef double radius = self.__parameters.queryQuasarRadius
		cdef double x = mmin.x
		cdef double y = mmin.y
		cdef bool hasVel = False #Will change later
		cdef double trueLuminosity = self.trueLuminosity
		cdef int aptLuminosity = 0
		with nogil:
			for i in range(0, resolution):
				x += stepX
				y += stepY
				aptLuminosity = self.query_data_length(x, y, radius)  # Incorrect interface
				yAxis[i] = (<double> aptLuminosity)/trueLuminosity
				if hasVel:
					with gil:
						self.__parameters.galaxy.moveStars(self.__parameters.dt)
						self.reconfigure()
		return yAxis
	
	def makeLightCurve(self,mmin, mmax, resolution):
		return self.makeLightCurve_helper(mmin,mmax,resolution)

		
	
	
	cpdef makeMagMap(self, object center, object dims, object resolution, object signal, object signalMax): #######Possibly slow implementation. Temporary
		########################## I STILL WANT TO SEE IF CAN MAKE MAGMAP FROM THE SOURCEPLANE RAY TRACE LOCATIONS, BUT IN THE MEANTIME
		########################## I'M DOING IT THE OLD-FASHIONED WAY #################################################################
		cdef int resx = <int> resolution.x
		cdef int resy = <int> resolution.y
		cdef np.ndarray[np.float64_t, ndim=2] retArr = np.ndarray((resx,resy), dtype=np.float64)
		cdef double stepX = dims.to('rad').x / resolution.x
		cdef double stepY = dims.to('rad').y / resolution.y
		cdef int i = 0
		cdef int j = 0
		cdef double x = 0
		cdef double y = 0
		# self.__parameters.galaxy.update(center=center)
		start = center - dims/2
		cdef double x0 = start.to('rad').x
		cdef double y0 = start.to('rad').y+dims.to('rad').y
		cdef double radius = self.__parameters.queryQuasarRadius
		cdef double trueLuminosity = self.trueLuminosity
		for i in prange(0,resx,nogil=True,schedule='guided',num_threads=self.core_count):
			if i % 10 == 0:
				with gil:
					signal.emit(i)
			for j in range(0,resy):
				retArr[i,j] = (<double> self.query_data_length(x0+i*stepX,y0-stepY*j,radius))/trueLuminosity
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



	def updateParameters(self, parameters,autoRecalculate = True):
		"""Provides an interface for updating the parameters describing the lensed system to be modeled.

		If the new system warrants a recalculation of spatial data, will call the function 'reconfigure' automatically"""
		if self.__parameters is None:
			self.__parameters = parameters
			if self.__parameters.galaxy.percentStars > 0 and self.__parameters.galaxy.stars == []:
				self.__parameters.regenerateStars()
			if autoRecalculate:
				self.reconfigure()
			else:
				self.needsReconfiguring = True
		elif not self.__parameters.isSimilar(parameters):
			self.__parameters.update(canvasDim = parameters.canvasDim)
			if self.__parameters.isSimilar(parameters):
				self.__parameters = parameters
				if self.__parameters.galaxy.percentStars > 0 and self.__parameters.galaxy.stars == []:
					self.__parameters.regenerateStars()
			else:
				self.__parameters = parameters
			if autoRecalculate:
				self.reconfigure()
			else:
				self.needsReconfiguring = True
		else:
			parameters.setStars(self.__parameters.stars)
			self.__parameters = parameters
