from __future__ import division
import numpy as np
cimport numpy as np
from WrappedTree_old import WrappedTree
from stellar import Galaxy
from stellar import Quasar
from Configs import Configs 
from astropy.cosmology import WMAP7 as cosmo
from Vector2D import Vector2D
from Vector2D import zeroVector
import time
from astropy import constants as const
from astropy import units as u
import math
import pyopencl as cl
import pyopencl.tools
import os
from SpatialTree cimport SpatialTree, Pixel
from libcpp.vector cimport vector
import random
from PyQt5 import QtGui, QtCore
import cython
cimport engineHelper
import ctypes
from libc.math cimport sin, cos, atan2, sqrt


cdef class Engine_cl:
	cdef:
		__parameters
		__preCalculating

		public double time
		__trueLuminosity
		__tree
		public img
		__imgColors
		np.ndarray __data_array

	cdef ray_trace_gpu(self,use_GPU)
	cpdef reconfigure(self)
	cpdef getFrame(self)
	cpdef getMagnification(self)
	cdef cythonMakeLightCurve(self,mmin, mmax,resolution,canvas, progressBar, smoothing)
