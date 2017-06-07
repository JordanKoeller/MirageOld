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

from Utility import Vector2D
from Utility import zeroVector
import pyopencl as cl


from libcpp.vector cimport vector
from libcpp cimport bool
from libc.math cimport sin, cos, atan2, sqrt



cdef class Engine:
	cdef:
		__parameters
		bool __preCalculating
		public double time
		__trueLuminosity

	cdef ray_trace_gpu(self)
	cpdef getMagnification(self, pixelCount)
	cpdef visualize(self)
	cdef makeLightCurve(self, object mmin, object mmax, int resolution)
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil
	cdef ray_trace_cpu(self)

