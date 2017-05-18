from Drawer cimport ImageDrawer
cimport numpy as np 
cdef class LensedImageDrawer(ImageDrawer):
	# cdef signal
	# cdef object pixmap
	# cdef object drawImage(self,np.ndarray[np.int8_t, ndim=2] pixels, object pixmap=*)

	# cdef object draw(self, object parameters, np.ndarray[np.int32_t, ndim=2] pixels)
	cpdef draw(self,object args)

	cdef void __drawTrackers(self,np.ndarray[np.uint8_t,ndim=2] canvas, object parameters)

	cdef void __drawEinsteinRadius(self,np.ndarray[np.uint8_t,ndim=2] canvas,object parameters)
