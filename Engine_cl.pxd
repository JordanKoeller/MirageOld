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
		public __calculating 
		public __needsReconfiguring
		public double time
		public double __einsteinRadius
		public int trueLuminosity
		public __quasar
		public __galaxy
		public __configs
		public dL
		public dLS
		public dS 
		public tree
		public img
		# public pixmap
		np.ndarray data_array
		# public byteArray
		# vector[]

	cpdef reConfigure(self)
	cpdef start(self, canvas)
	cpdef restart(self)
	cpdef pause(self)
	cdef drawFrame(self,canvas)
	cdef calcDeflections(self)
	cdef queryTree(self,position)
	cdef ray_trace_gpu(self)
	cdef buildTree(self, data)
	cpdef getMagnification(self)

	# cdef vector[Pixel] queryTree(self,x,y,r)
