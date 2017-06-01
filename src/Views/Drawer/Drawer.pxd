cimport numpy as np 
import numpy as np 


cdef class Drawer:
	cdef signal
	cpdef draw(self,object args)

cdef class ImageDrawer(Drawer):
	cdef object pixmap
	cdef object drawImage(self,np.ndarray[np.uint8_t, ndim=2] pixels, object pixmap=*)

cdef class PlotDrawer(Drawer):
	cdef np.float64_t[:] xAxis
	cdef np.float64_t[:] yAxis
	cdef int index
	cdef append(self, double y, double x=*)
	cdef plotAxes(self, np.ndarray[np.float64_t, ndim=1] x, np.ndarray[np.float64_t, ndim=1] y)

cdef class CompositeDrawer:
	cdef ImageDrawer imgDrawer 
	cdef PlotDrawer plotDrawer 
	cpdef draw(self, object imgArgs, object plotArgs)
	cpdef reset(self)
