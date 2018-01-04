from .PointerGrid cimport PointerGrid
import numpy as np
cimport numpy as np 

cpdef PointerGridWrapper construct(np.ndarray[np.float64_t,ndim=2] data):
	cdef double xx = data[:,0][0]
	cdef double yy = data[:,1][0]
	cdef int node_count = 7*len(data)
	cdef int ndim = 2
	cdef int h = 1
	cdef int w = len(data)
	return PointerGridWrapper(xx,yy,w,h,ndim,node_count)

cdef class PointerGridWrapper:
	
	def __cinit__(self,double xx, double yy, int w, int h, int ndim, int node_count):
		cdef double* x = &xx
		cdef double* y = &yy
		self._pointerGrid = PointerGrid(x,y,w,h,ndim,node_count)

	cpdef find_within_count(self,double x, double y, double r):
		return self._pointerGrid.find_within_count(x,y,r)