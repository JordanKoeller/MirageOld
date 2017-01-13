
cimport numpy as np
from stellar import Galaxy
from stellar import Quasar
from Configs import Configs 
from astropy.cosmology import WMAP7 as cosmo
from Vector2D import Vector2D
import time
from astropy import constants as const
import math
# from libcpp.vector cimport vector
import pyopencl as cl
from SpatialTree cimport SpatialTree


cdef class Engine_cl:
	cdef:
		public __preCalculating
		# public __calculating 
		public __needsReconfiguring
		public double time
		public double __einsteinRadius
		public int __trueLuminosity
		public __quasar
		public __galaxy
		public __configs
		public __dL
		public __dLS
		public __dS 
		public __tree
		public img
		# public pixmap
		np.ndarray __data_array
		# public byteArray
		# vector[]

	cpdef reconfigure(self)
	# cpdef start(self, canvas)
	# cpdef restart(self)
	# cpdef pause(self)
	cpdef drawFrame(self)
	cdef calcDeflections(self)
	cdef queryTree(self,position)
	cdef ray_trace_gpu(self,use_GPU)
	cdef buildTree(self, data)
	cpdef getMagnification(self)

	# cdef vector[Pixel] queryTree(self,x,y,r)
