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
from Utility.Grid cimport Grid
from Utility.Grid cimport Pixel
from Engine cimport Engine
from libcpp cimport bool

cdef class Engine_Grid(Engine):

	def __init__(self, parameter=Parameters()):
		Engine.__init__(self,parameter)

	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray):
		cdef int hw
		hw = xArray.shape[0]
		cdef int x, y
		cdef int nodeSz = hw * hw
		cdef pair[double, double] sp 
		cdef pair[int, int] pp
		x = 0
		y = 0
		cdef vector[pair[pair[double, double], pair[int, int]]] tmpVect
		for x in range(0, hw):
			for y in range(0, hw):
				sp = pair[double, double](xArray[x, y], yArray[x, y])
				pp = pair[int, int](< int > x, < int > y)
				tmpVect.push_back(pair[pair[double, double], pair[int, int]](sp, pp))
		self.__grid = Grid(tmpVect.begin(), tmpVect.end(), nodeSz)

	cdef vector[Pixel] query_data(self, double x, double y, double radius):
		cdef vector[Pixel] ret = self.__grid.find_within(x, y, radius)
		return ret

	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame(self):
		if self.__needsReconfiguring:
			self.reconfigure_grid()
		while self.__preCalculating:
			print("waiting")
		cdef double qx = <double> self.__parameters.queryQuasarX
		cdef double qy = <double> self.__parameters.queryQuasarY
		cdef double qr = <double> self.__parameters.queryQuasarRadius
		cdef vector[Pixel] ret = self.query_data(qx,qy,qr)
		cdef int retf = ret.size()
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
		for i in range(0, retf):
			fret[i][0] = ret[i].pixelX
			fret[i][1] = ret[i].pixelY
		return fret  # self.__tree.query_point(self.__parameters.quasar.observedPosition.x+gX,self.__parameters.quasar.observedPosition.y+gY,self.__parameters.quasar.radius.value)
