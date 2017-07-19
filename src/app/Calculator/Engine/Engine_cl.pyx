# distutils: language=c++
# cython: profile=True
from __future__ import division
import numpy as np
cimport numpy as np
from Utility import WrappedTree
from Models.Stellar.Galaxy import Galaxy
from Models.Stellar.Quasar import Quasar
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
from Models.Parameters.Parameters import Parameters
from scipy import interpolate
from libcpp.pair cimport pair
# from Utility.Grid cimport Grid
# from Utility.Grid cimport Pixel
from Utility.SpatialTree cimport SpatialTree, Pixel
from libcpp cimport bool

cdef class Engine_cl:

	def __init__(self, parameter=Parameters()):
		self.__parameters = parameter
		self.__preCalculating = False
		self.time = 0.0
		self.__trueLuminosity = math.pi * (self.__parameters.quasar.radius.value / self.__parameters.dTheta.value) ** 2
		self.__needsReconfiguring = True

	@property
	def parameters(self):
		return self.__parameters

	def ray_trace(self, use_GPU=False):
		return self.ray_trace_gpu(False)


	cdef ray_trace_gpu(self, use_GPU):
		# print(self.__parameters)
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		os.environ['PYOPENCL_CTX'] = '2'
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef double dTheta = self.__parameters.dTheta.value
		cdef np.ndarray result_nparray_x = np.ndarray((width, height), dtype=np.float64)
		cdef np.ndarray result_nparray_y = np.ndarray((width, height), dtype=np.float64)
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

		# read and compile opencl kernel
		prg = cl.Program(context, open('Calculator/engine_helper.cl').read()).build()
		prg.ray_trace(queue, (width, height), None,
			stars_buffer_mass,
			stars_buffer_x,
			stars_buffer_y,
			np.int32(len(stars_nparray_x)),
			np.float64((4 * const.G / (const.c * const.c)).to("lyr/solMass").value),
			np.float64(4 * math.pi * (const.c ** -2).to('s2/km2').value),
			np.float64(self.__parameters.galaxy.shear.magnitude),
			np.float64(self.__parameters.galaxy.shear.angle.value),
			np.float64(self.__parameters.galaxy.velocityDispersion.value),
			np.float64(self.__parameters.galaxy.angDiamDist.value),
			np.float64(self.__parameters.quasar.angDiamDist.value),
			np.float64(self.__parameters.dLS.value),
			np.int32(width),
			np.int32(height),
			np.float64(self.__parameters.dTheta.value),
			np.float64(self.__parameters.galaxy.position.to('rad').x),
			np.float64(self.__parameters.galaxy.position.y),
			result_buffer_x,
			result_buffer_y)

		cl.enqueue_copy(queue, result_nparray_x, result_buffer_x)
		cl.enqueue_copy(queue, result_nparray_y, result_buffer_y)
		print("Time Ray-Tracing = " + str(time.clock() - begin))
		return (result_nparray_x, result_nparray_y)

	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cdef build_grid(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray):
		cdef int hw
		hw = xArray.shape[0]
		cdef int x, y
		cdef int nodeSz = hw * hw
		cdef pair[double, double] sp 
		cdef pair[int, int] pp
		x = 0
		y = 0
		cdef vector[pair[pair[double, double], pair[int, int]]] tmpVect
		for x in range(0, hw):
			for y in range(0, hw):
				sp = pair[double, double](xArray[x, y], yArray[x, y])
				pp = pair[int, int](< int > x, < int > y)
				tmpVect.push_back(pair[pair[double, double], pair[int, int]](sp, pp))
		self.__grid = Grid(tmpVect.begin(), tmpVect.end(), nodeSz)

	cdef vector[Pixel] query_grid(self, double x, double y, double radius):
		cdef vector[Pixel] ret = self.__grid.find_within(x, y, radius)
		return ret

	cdef buildTree(self, data):
			self.__tree = SpatialTree()
			xvals = data[0]
			yvals = data[1]
			cdef int width = self.__configs.canvasDim.x
			cdef int height = self.__configs.canvasDim.y
			cdef double dS = self.dS
			cdef int i = 0
			cdef int j = 0
			for i in range(width):
					for j in range(height):
							self.__tree.insert(i,j,xvals[i,j],yvals[i,j])

	cpdef reconfigure_grid(self):
		begin = time.clock()
		self.__preCalculating = True
		# self.__tree = WrappedTree()
		finalData = self.ray_trace(use_GPU=True)
		self.build_grid(finalData[0], finalData[1])
		# self.__tree.setDataFromNumpies(finalData)
		self.__preCalculating = False
		self.__needsReconfiguring = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")

	cpdef reconfigure_tree(self):
		begin = time.clock()
		self.__preCalculating = True
		self.__tree = WrappedTree()
		finalData = self.ray_trace(use_GPU=True)
# 		self.build_grid(finalData[0], finalData[1])
		self.__tree.setDataFromNumpies(finalData)
		self.__preCalculating = False
		self.__needsReconfiguring = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")

	cpdef reconfigure_myTree(self):
		begin = time.clock()
		self.__preCalculating = True
		finalData = self.ray_trace(use_GPU=True)
# 		self.build_grid(finalData[0], finalData[1])
		self.build_my_tree(finalData)
		self.__preCalculating = False
		self.__needsReconfiguring = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")

	def calTheta(self):
		k = (4 * math.pi * (const.c ** -2).to('s2/km2').value * self.__parameters.dLS.value / self.__parameters.quasar.angDiamDist.value * self.__parameters.galaxy.velocityDispersion.value * self.__parameters.galaxy.velocityDispersion.value) + (self.__parameters.quasar.position - self.__parameters.galaxy.position).magnitude()
		theta = (k / (1 - (self.__parameters.dLS.value / self.__parameters.quasar.angDiamDist.value) * self.__parameters.galaxy.shearMag))
		theta2 = (k / (1 + (self.__parameters.dLS.value / self.__parameters.quasar.angDiamDist.value) * self.__parameters.galaxy.shearMag))
		return (theta, theta2)

	@property
	def tree(self):
		return self.__tree

	cpdef getMagnification(self):
		cdef a = np.float64 (self.__trueLuminosity)
		cdef b = np.float64 (self.__tree.query_point_count(self.__parameters.quasar.observedPosition.x, self.__parameters.quasar.observedPosition.y, self.__parameters.quasar.radius.value))
		return b / a

	def incrementTime(self, dt):
		self.time += dt 
		self.parameters.setTime(self.time)

	def setTime(self, t):
		self.time = t 
		self.parameters.setTime(t)

	
	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame_grid(self):
		if self.__needsReconfiguring:
			self.reconfigure_grid()
		while self.__preCalculating:
			print("waiting")
		cdef double qx = <double> self.__parameters.queryQuasarX
		cdef double qy = <double> self.__parameters.queryQuasarY
		cdef double qr = <double> self.__parameters.queryQuasarRadius
		cdef vector[Pixel] ret = self.query_myTree(qx,qy,qr)
		cdef int retf = ret.size()
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
		for i in range(0, retf):
			fret[i][0] = ret[i].pixelX
			fret[i][1] = ret[i].pixelY
		return fret  # self.__tree.query_point(self.__parameters.quasar.observedPosition.x+gX,self.__parameters.quasar.observedPosition.y+gY,self.__parameters.quasar.radius.value)

	
	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame_tree(self):
		if self.__needsReconfiguring:
			self.reconfigure_tree()
		while self.__preCalculating:
			print("waiting")
		cdef double qx = self.__parameters.queryQuasarX
		cdef double qy = self.__parameters.queryQuasarY
		cdef double qr = self.__parameters.queryQuasarRadius
		ret = self.tree.query_point(qx,qy,qr)
		cdef int retf = len(ret)
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((retf, 2), dtype=np.int32)
		for i in range(0, retf):
			fret[i][0] = ret[i][0]
			fret[i][1] = ret[i][1]
		return fret
	
	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame_myTree(self):
		if self.__needsReconfiguring:
			self.reconfigure_tree()
		while self.__preCalculating:
			print("waiting")
		cdef double qx = self.__parameters.queryQuasarX
		cdef double qy = self.__parameters.queryQuasarY
		cdef double qr = self.__parameters.queryQuasarRadius
		ret = self.tree.query_point(qx,qy,qr)
		cdef int retf = len(ret)
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((retf, 2), dtype=np.int32)
		for i in range(0, retf):
			fret[i].x = ret[i].x
			fret[i].y = ret[i].y
		return fret

	cdef cythonMakeLightCurve(self, mmin, mmax, resolution, progressBar, smoothing):
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
		cdef double gx = self.__parameters.galaxy.position.x
		cdef double gy = self.__parameters.galaxy.position.y
		for i in range(0, resolution):
			x += stepX
			y += stepY
			yAxis[i] = self.__tree.query_point_count(x + gx, y + gy, radius)
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

	def makeLightCurve(self, mmin, mmax, resolution=200, canvas=None, progressBar=None, smoothing=True):
		return self.cythonMakeLightCurve(mmin, mmax, resolution, progressBar, smoothing)


	def updateParameters(self, parameters):
		if self.__parameters is None:
			self.__parameters = parameters
			if self.__parameters.galaxy.center != zeroVector and self.__parameters.galaxy.percentStars > 0:
				self.__parameters.generateStars()
			self.__needsReconfiguring = True
		elif not self.__parameters.isSimilar(parameters):
			self.__parameters = parameters
			if self.__parameters.galaxy.center != zeroVector and self.__parameters.galaxy.percentStars > 0:
				self.__parameters.generateStars()
			self.__needsReconfiguring = True
		else:
			parameters.setStars(self.__parameters.stars)
			self.__parameters = parameters




