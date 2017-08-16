from __future__ import division

import ctypes

import cython

import numpy as np


cimport numpy as np
from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair
from Utility.SpatialTree_new cimport SpatialTree
from Utility.SpatialTree_new cimport Pixel
from Calculator.Engine.Engine cimport Engine


cdef class Engine_Quadtree(Engine):
	cdef SpatialTree __spatialTree
	
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray)
	cdef vector[Pixel] query_data(self, double x, double y, double radius)
	cpdef getFrame(self)
	cpdef reconfigure(self)

