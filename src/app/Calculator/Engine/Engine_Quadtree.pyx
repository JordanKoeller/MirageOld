# distutils: language=c++
# cython: profile=True
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
from libc.math cimport sin, cos, atan2, sqrt
from libcpp.pair cimport pair
from Utility.SpatialTree_new cimport SpatialTree
from Utility.SpatialTree_new cimport Pixel
from Calculator.Engine.Engine cimport Engine
from libcpp cimport bool

cdef class Engine_Quadtree(Engine):

	def __init__(self, parameter=Parameters()):
		Engine.__init__(self,parameter)

	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray):
		cdef int hw
		hw = xArray.shape[0]
		cdef int x, y
		x = 0
		y = 0
		print("initlaizeing")
		# self.__spatialTree = SpatialTree()
		print("Done, now inserting")
		for x in range(0, hw):
			for y in range(0, hw):
				self.__spatialTree.insert(x,y,xArray[x, y], yArray[x, y])

	cdef vector[Pixel] query_data(self, double x, double y, double radius):
		cdef vector[Pixel] ret = self.__spatialTree.query_point(x, y, radius)
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
		cdef vector[Pixel] ret = self.query_data(qx,qy,qr)
		cdef int retf = ret.size()
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
		for i in range(0, retf):
			fret[i][0] = ret[i].x
			fret[i][1] = ret[i].y
		return fret  # self.__tree.query_point(self.__parameters.quasar.observedPosition.x+gX,self.__parameters.quasar.observedPosition.y+gY,self.__parameters.quasar.radius.value)

	def visualize(self):
		x,y = self.ray_trace(use_GPU=True)
		extrema  = [abs(x.min()),abs(y.min()),abs(x.max()),abs(y.max())]
		# for i in extrema:
		# 	print(i)
		extreme = max(extrema)
		x *= (1200/extreme)
		y *= (1200/extreme)
		img = np.ones((1200,1200))
		for i in range(0,x.shape[0]):
			for j in range(0,y.shape[1]):
				img[int(x[i,j]),int(y[i,j])] = 0
		return img

