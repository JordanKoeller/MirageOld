from __future__ import division

import ctypes

import cython

import numpy as np


cimport numpy as np
from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair
from ...Utility.PointerGrid cimport PointerGrid
from ...Utility.WindowGrid cimport WindowGrid
# from Utility.Grid cimport Pixel
from .Engine cimport Engine


cdef class Engine_Windowed(Engine):
	cdef WindowGrid[PointerGrid] __grid
	cdef  gridData
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray,int binsize)
	cdef vector[pair[int,int]] query_data(self, double x, double y, double radius) nogil
	cpdef getFrame(self,object x=*,object y=*,object r=*)
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil
	cpdef windowed_magMap(self, object center, object dims, object resolution, object signal, object signalMax, numChunk=*)
