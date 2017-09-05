from __future__ import division
import numpy as np
cimport numpy as np
from libcpp.vector cimport vector
from libcpp cimport bool
import cython
import ctypes
from libcpp.pair cimport pair
from .Engine cimport Engine


cdef class Engine_BruteForce(Engine):
	cdef vector[pair[int,int]] query_data(self, double x, double y, double radius)
	cpdef getFrame(self)
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil
	cpdef query_raw_size(self,double x,double y,double r)

