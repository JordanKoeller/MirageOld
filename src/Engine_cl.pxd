from __future__ import division
import numpy as np
cimport numpy as np
from Utility import WrappedTree
from Stellar import Galaxy
from Stellar import Quasar
from astropy.cosmology import WMAP7 as cosmo
from Utility import Vector2D
from Utility import zeroVector
import time
from astropy import constants as const
from astropy import units as u
import math
import pyopencl as cl
import pyopencl.tools
import os
from libcpp.vector cimport vector
import random
from PyQt5 import QtGui, QtCore
import cython
import ctypes
from libc.math cimport sin, cos, atan2, sqrt
from Parameters import Parameters
from scipy import interpolate
from libcpp.pair cimport pair
from Utility.Grid cimport Grid
from Utility.Grid cimport Pixel


cdef class Engine_cl:
	cdef:
		__parameters
		__preCalculating
		__needsReconfiguring

		public double time
		__trueLuminosity
		__tree
		public img
		__imgColors
		np.ndarray __data_array
		Grid __grid

	cdef ray_trace_gpu(self,use_GPU)
	cdef build_grid(self,xArray,yArray)
	cdef vector[Pixel] query_grid(self,double x, double y, double radius)
	cpdef reconfigure(self)
	cpdef getFrame(self)
	cpdef getMagnification(self)
	cdef cythonMakeLightCurve(self,mmin, mmax,resolution, progressBar, smoothing)
