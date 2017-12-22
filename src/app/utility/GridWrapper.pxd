from .PointerGrid cimport PointerGrid
cimport numpy as np
import numpy as np
cpdef PointerGridWrapper construct(np.ndarray[np.float64_t,ndim=2] data)

cdef class PointerGridWrapper:
	cdef PointerGrid _pointerGrid

	cpdef find_within_count(self,double x, double y, double r)