

from scipy.spatial cimport cKDTree as Tree
cimport numpy as np
import time
from Vector2D import Vector2D

cdef class WrappedTree:
	cdef:
		Tree tree
		np.ndarray[dtype = np.float32_t, ndim = 2] array

	cpdef np.ndarray query_tree(self, double x, double y, double radius)
	cdef set_Data_Helper(self, xVals, yVals)