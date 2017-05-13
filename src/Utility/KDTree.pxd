from scipy import spatial as sp
from Utility import Vector2D
import time
from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.pair cimport pair
import numpy as np
cimport numpy as np

cdef class KDTree:
	cdef map[int,pair[int,int]] __map
	cdef __tree
	cpdef insertAll(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray)
	cpdef vector[pair[int,int]] query_point(self, double x, double y, double radius)
