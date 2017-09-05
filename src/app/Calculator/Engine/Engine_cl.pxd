from __future__ import division

import ctypes
import math
import os
import random
import time

from PyQt5 import QtGui, QtCore
from astropy import constants as const
from astropy import units as u
from astropy.cosmology import WMAP7 as cosmo
import cython
import pyopencl.tools
from scipy import interpolate

from Models.Parameters.Parameters import Parameters
from Models.Stellar.Galaxy import Galaxy
from Models.Stellar.Quasar import Quasar
from Utility import Vector2D
from Utility import WrappedTree
from Utility import zeroVector
import numpy as np
import pyopencl as cl


cimport numpy as np
from libcpp.vector cimport vector
from libcpp cimport bool
from libc.math cimport sin, cos, atan2, sqrt
from libcpp.pair cimport pair
from Utility.Grid cimport Grid
from Utility.Grid cimport Pixel


cdef class Engine_cl:
	cdef:
		__parameters
		bool __preCalculating
		bool __needsReconfiguring

		public double time
		__trueLuminosity
		__tree
		np.ndarray __data_array
		Grid __grid

	cdef ray_trace_gpu(self,use_GPU)
	cdef build_grid(self,np.ndarray[np.float64_t, ndim=2] xArray,np.ndarray[np.float64_t, ndim=2] yArray)
	cdef vector[Pixel] query_grid(self,double x, double y, double radius)
	cpdef getFrame_myTree(self)
	cpdef reconfigure_myTree(self)
	cpdef reconfigure_grid(self)
	cpdef reconfigure_tree(self)
	cpdef getFrame_grid(self)
	cpdef getFrame_tree(self)
	cpdef getMagnification(self)
	cdef cythonMakeLightCurve(self,mmin, mmax,resolution, progressBar, smoothing)
