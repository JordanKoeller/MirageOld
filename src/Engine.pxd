from __future__ import division
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
from libcpp cimport bool
import cython
import ctypes
from libc.math cimport sin, cos, atan2, sqrt
from Parameters import Parameters
from scipy import interpolate



cdef class Engine:
	cdef:
		__parameters
		bool __preCalculating
		bool __needsReconfiguring
		public double time
		__trueLuminosity

	cdef ray_trace_gpu(self,use_GPU)
	cpdef getMagnification(self)
	cdef cythonMakeLightCurve(self,mmin, mmax,resolution, progressBar, smoothing)