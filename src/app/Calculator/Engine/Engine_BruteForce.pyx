from __future__ import division

import ctypes

import cython

import numpy as np


cimport numpy as np
from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair
from ...Utility.PointerGrid cimport PointerGrid
# from Utility.Grid cimport Pixel
from .Engine cimport Engine

cdef extern from "ShapeQuery.hpp":
	vector[pair[int,int]] query_shape(double* x, double* y, int width, double qx, double qy, double qr) nogil

cdef class Engine_BruteForce(Engine):


	cdef vector[pair[int,int]] query_data(self, double x, double y, double radius):
		cdef np.ndarray[np.float64_t, ndim=2] xVals,yVals
		xVals,yVals = self.ray_trace()
		# cdef double dx, dy, r2
		cdef int sz = xVals.shape[0]
		cdef double* xdat = <double*> xVals.data
		cdef double* ydat = <double*> yVals.data
		# cdef int i = 0
		# cdef int j = 0
		# r2 = radius*radius
		cdef vector[pair[int,int]] ret
		with nogil:
			ret = query_shape(xdat,ydat,sz,x,y,radius)
		xVals.shape
		yVals.shape
		return ret
	
	cpdef query_raw_size(self,double x,double y,double radius):
		cdef np.ndarray[np.float64_t, ndim=2] xVals,yVals
		xVals,yVals = self.ray_trace_gpu_raw()
		# cdef double dx, dy, r2
		cdef int sz = xVals.shape[0]
		cdef double* xdat = <double*> xVals.data
		cdef double* ydat = <double*> yVals.data
		# cdef int i = 0
		# cdef int j = 0
		# r2 = radius*radius
		cdef vector[pair[int,int]] ret
		with nogil:
			ret = query_shape(xdat,ydat,sz,x,y,radius)
		xVals.shape
		yVals.shape
		return ret.size()


	cpdef getFrame(self):
		qx = self.parameters.queryQuasarX
		qy = self.parameters.queryQuasarY
		qr = self.parameters.queryQuasarRadius
		cdef vector[pair[int,int]] pixelLocs = self.query_data(qx,qy,qr)
		cdef int i = 0
		cdef np.ndarray[np.int32_t,ndim=2] ret = np.ndarray((pixelLocs.size(),2),dtype=np.int32)
		cdef int sz = pixelLocs.size()
		for i in range(0,sz):
			ret[i,0] = pixelLocs[i].first
			ret[i,1] = pixelLocs[i].second
		return ret

	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil:
		with gil:
			return self.query_data(x,y,radius).size()

	def reconfigure(self):
		pass

