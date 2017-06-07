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

# from Models import Galaxy
# from Models import Parameters
# from Models import Quasar
from Utility import Vector2D
# from Utility import WrappedTree
from Utility import zeroVector
from Views.Drawer.Drawer import PlotDrawer
import numpy as np
import pyopencl as cl


cimport numpy as np
from libcpp.vector cimport vector
from libc.math cimport sin, cos, atan2, sqrt
from libcpp.pair cimport pair
from Utility.Grid cimport Grid
from Utility.Grid cimport Pixel
from Calculator.Engine.Engine cimport Engine
from libcpp cimport bool

cdef class Engine_Grid(Engine):

	"""
	Impliments the Engine class with a grid spatial hashing data structure for fast lensing system calculations, along with fast queries of the system and 
	production of light curves or magnification maps. 
	"""
	def __init__(self, parameter=None):
		Engine.__init__(self,parameter)

	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray,int binsize):
		"""Builds the spatial data structure, based on the passed in numpy arrays representing the x and y values of each
			pixel where it intersects the source plane after lensing effects have been accounted for."""
		cdef int w = xArray.shape[0]
		cdef int h = xArray.shape[1]
		cdef double* x = <double*> xArray.data
		cdef double* y = <double*> yArray.data
		with nogil:
			self.__grid = Grid(x,y,w,h,binsize)

	cdef vector[Pixel] query_data(self, double x, double y, double radius) nogil:
		"""Returns all rays that intersect the source plane within a specified radius of a location on the source plane."""
		cdef vector[Pixel] ret = self.__grid.find_within(x, y, radius)
		return ret
	
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil:
		return self.query_data(x,y,radius).size()

	def reconfigure(self):
		begin = time.clock()
		self.__preCalculating = True
		finalData = self.ray_trace(use_GPU=True)
		self.build_data(finalData[0], finalData[1],int(finalData[0].shape[0]**2/2))
		del(finalData)
		self.__preCalculating = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")
# 		time.sleep(3)


	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame(self):
		"""
		Returns a 2D numpy array, containing the coordinates of pixels illuminated by the source specified in the system's parameters.
		"""
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
		"""
		Deprecated
		"""
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
