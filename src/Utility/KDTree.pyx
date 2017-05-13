from scipy import spatial as sp
from Utility import Vector2D
import time
from libcpp.map cimport map
from libcpp.vector cimport vector


cdef class KDTree:
	# cdef map[int,pair[int,int]] __map
	# cdef __tree
	cpdef insertAll(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray):
		cdef int h = xArray.shape[0]
		cdef int w = xArray.shape[1]
		cdef int i = 0
		cdef int j = 0
		for i in range(0,w):
			for j in range(0,h):
				

	cpdef vector[pair[int,int]] query_point(self, double x, double y, double radius)
