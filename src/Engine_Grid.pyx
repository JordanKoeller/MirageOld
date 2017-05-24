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
from Drawer.Drawer import PlotDrawer

cdef class Engine_Grid(Engine):

	def __init__(self, parameter=Parameters()):
		Engine.__init__(self,parameter)

	# @cython.boundscheck(False)  # turn off bounds-checking for entire function
	# @cython.wraparound(False)
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray,int binsize):
		cdef int hw
		hw = xArray.shape[0]
		cdef int x, y
		cdef int nodeSz = hw * hw
		cdef pair[double, double] sp 
		cdef pair[int, int] pp
		cdef vector[pair[pair[double, double], pair[int, int]]] tmpVect
		with nogil:
			x = 0
			y = 0
			for x in range(0, hw):
				for y in range(0, hw):
					sp = pair[double, double](xArray[x, y], yArray[x, y])
					pp = pair[int, int](< int > x, < int > y)
					tmpVect.push_back(pair[pair[double, double], pair[int, int]](sp, pp))
			self.__grid = Grid(tmpVect.begin(), tmpVect.end(), binsize)

	cdef vector[Pixel] query_data(self, double x, double y, double radius) nogil:
		cdef vector[Pixel] ret = self.__grid.find_within(x, y, radius)
		return ret

	cpdef reconfigure(self):
		begin = time.clock()
		self.__preCalculating = True
		finalData = self.ray_trace(use_GPU=True)
		self.build_data(finalData[0], finalData[1],int(finalData[0].shape[0]**2/2))
		self.__preCalculating = False
		self.__needsReconfiguring = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")
		print(self.__parameters)


	# @cython.boundscheck(False)  # turn off bounds-checking for entire function
	# @cython.wraparound(False)
	cpdef getFrame(self):
		if self.__needsReconfiguring:
			self.reconfigure()
		while self.__preCalculating:
			print("waiting")
		cdef double qx = self.__parameters.queryQuasarX
		cdef double qy = self.__parameters.queryQuasarY
		cdef double qr = self.__parameters.queryQuasarRadius
		cdef vector[Pixel] ret = self.query_data(qx,qy,qr)
		cdef int retf = ret.size()
		cdef int i = 0
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
		with nogil:
			for i in range(0, retf):
				fret[i,0] = <int> ret[i].pixelX
				fret[i,1] = <int> ret[i].pixelY
		return fret

	def gridTest(self,binsizes,queryPerTest,curveSignal,barSignal):
		x,y = self.ray_trace(use_GPU=False)
		drawer = PlotDrawer(curveSignal)
		counter = 0
		yvals= []
		for i in binsizes:
			grid = self.build_data(x,y,int(i))
			timer = time.clock()
			for i in range(0,queryPerTest):
				self.getFrame()
			counter += 1
			barSignal.emit(counter)
			delta = time.clock() - timer
			yvals.append(delta/queryPerTest)
		drawer.draw(binsizes,yvals)
