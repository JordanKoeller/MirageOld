
cimport numpy as np
from stellar import Galaxy
from stellar import Quasar
from Configs import Configs 
from astropy.cosmology import WMAP7 as cosmo
from Vector2D import Vector2D
import time
from astropy import constants as const
import math
import pyopencl as cl
from SpatialTree cimport SpatialTree, Pixel
from libcpp.vector cimport vector


cdef class Engine_cl:
	cdef:
		__preCalculating
		__needsReconfiguring
		__quasar
		__galaxy
		__configs

		public double time
		double __einsteinRadius
		long int __trueLuminosity
		__dLS

		__tree
		public img
		np.ndarray __data_array

	cdef calcDeflections(self)
	cdef queryTree(self,position)
	cdef ray_trace_gpu(self,use_GPU)
	cdef buildTree(self, data)

	cpdef reconfigure(self)
	cpdef getFrame(self)
	cpdef getMagnification(self)