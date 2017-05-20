# distutils: language=c++
# cython: profile=True
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
from Engine cimport Engine
from libcpp cimport bool

cdef class Engine_KDTree(Engine):

	def __init__(self, parameter=Parameters()):
		Engine.__init__(self,parameter)

	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray):
		self.__data = WrappedTree()
		self.__data.setDataFromNumpies([xArray,yArray])

	cdef query_data(self, double x, double y, double radius):
		ret = self.__data.query_point(x, y, radius)
		return ret

	cpdef reconfigure(self):
		begin = time.clock()
		self.__preCalculating = True
		finalData = self.ray_trace(use_GPU=True)
		self.build_data(finalData[0], finalData[1])
		self.__preCalculating = False
		self.__needsReconfiguring = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")


	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame(self):
		if self.__needsReconfiguring:
			self.reconfigure()
		while self.__preCalculating:
			print("waiting")
		cdef double qx = <double> self.__parameters.queryQuasarX
		cdef double qy = <double> self.__parameters.queryQuasarY
		cdef double qr = <double> self.__parameters.queryQuasarRadius
		ret = self.query_data(qx,qy,qr)
		# cdef int retf = len(ret)
		# cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
		# for i in range(0, retf):
		# 	fret[i][0] = ret[i].x
		# 	fret[i][1] = ret[i].y
		return ret  # self.__tree.query_point(self.__parameters.quasar.observedPosition.x+gX,self.__parameters.quasar.observedPosition.y+gY,self.__parameters.quasar.radius.value)
