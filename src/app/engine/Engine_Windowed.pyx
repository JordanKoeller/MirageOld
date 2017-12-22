

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
from scipy import interpolate

from ...Utility import Vector2D
from ...Utility import zeroVector
import numpy as np
cimport numpy as np
from libcpp.vector cimport vector
from libc.math cimport sin, cos, atan2, sqrt
from libcpp.pair cimport pair
from ...Utility.PointerGrid cimport PointerGrid
from ...Utility.WindowGrid cimport WindowGrid
from .Engine cimport Engine
from libcpp cimport bool
from libc.stdlib cimport malloc, free

from cython.parallel import prange


cdef class Engine_Windowed(Engine):

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
		cdef int nd = 2
		cdef double* x = <double*> xArray.data 
		cdef double* y = <double*> yArray.data
		with nogil:
			self.__grid = WindowGrid[PointerGrid](x,y,h,w,nd)

	cdef vector[pair[int,int]] query_data(self, double x, double y, double radius) nogil:
		"""Returns all rays that intersect the source plane within a specified radius of a location on the source plane."""
		cdef vector[pair[int,int]] ret = self.__grid.find_within(x, y, radius)
		return ret
	
	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil:
		return self.__grid.find_within_count(x, y, radius)

	def reconfigure(self):
		print("Reconfiguring")
		print(self.__parameters)
		self.__grid = WindowGrid[PointerGrid]()
		begin = time.clock()
		self.__preCalculating = True
		finalData = self.ray_trace(use_GPU=True)
		self.build_data(finalData[0], finalData[1],int(2*finalData[0].shape[0]**2))
		del(finalData)
		self.__preCalculating = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")
# 		time.sleep(3)


	@cython.boundscheck(False)  # turn off bounds-checking for entire function
	@cython.wraparound(False)
	cpdef getFrame(self,object x=None,object y=None,object r=None):
		"""
		Returns a 2D numpy array, containing the coordinates of pixels illuminated by the source specified in the system's parameters.
		"""
		#Possible optimization by using vector data rather than copy?
		while self.__preCalculating:
			print("waiting")
			time.sleep(0.1)
		begin = time.clock()
		cdef double qx = 0
		cdef double qy = 0
		cdef double qr = 0
		if x == None:
			qx = self.__parameters.queryQuasarX
			qy = self.__parameters.queryQuasarY
			qr = self.__parameters.queryQuasarRadius
		else:
			qx = x
			qy = y
			qr = r
		cdef vector[pair[int,int]] ret = self.query_data(qx,qy,qr)
		cdef int retf = ret.size()
		cdef int i = 0
		cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
		with nogil:
			for i in range(0, retf):
				fret[i,0] = <int> ret[i].first
				fret[i,1] = <int> ret[i].second
		return fret

	cpdef makeMagMap(self, object center, object dims, object resolution, object signal, object signalMax):
		return self.windowed_magMap(center,dims,resolution,signal,signalMax,25)


	cdef int _noGILMin(self,int i, int j) nogil:
		if i < j: return i
		if j < i: return j


	cpdef windowed_magMap(self, object center, object dims, object resolution, object signal, object signalMax, numChunk = 25):
	
		cdef int resx = <int> resolution.x
		cdef int resy = <int> resolution.y
		cdef np.ndarray[np.float64_t, ndim=2] retArr = np.ndarray((resx,resy), dtype=np.float64)
		cdef double stepX = dims.to('rad').x / resolution.x
		cdef double stepY = dims.to('rad').y / resolution.y
		cdef int i = 0
		cdef int j = 0
# 		cdef int rootChunk = math.sqrt(numChunk)
# 		cdef int chunkXStep = int(resx/rootChunk)
# 		cdef int chunkYStep = int(resy/rootChunk)
# 		cdef double x = 0
# 		cdef double y = 0
# 		cdef int chunkY = 0
# 		cdef int chunkX = 0
		start = center - dims/2
		cdef double x0 = start.to('rad').x
		cdef double y0 = start.to('rad').y
		cdef double radius = self.__parameters.queryQuasarRadius
		cdef double trueLuminosity = self.trueLuminosity
		tl = pair[double,double](x0-2*radius,y0+2*radius)
		br = pair[double,double](x0+dims.to('rad').x+2*radius,y0-dims.to('rad').y-2*radius)
		self.__grid.set_corners(tl,br)
# 		print("Now onto for looping")
		for i in prange(0,resx,nogil=True,schedule='guided',num_threads=self.core_count):
			for j in range(0,resy):
				retArr[i,j] = (<double> self.query_data_length(x0+i*stepX,y0+j*stepY,radius))/trueLuminosity
		return retArr
# 		for chunkX in range(0,resx,chunkXStep):
# 			for chunkY in range(0,resy,chunkYStep):
# 				tl = pair[double,double](x0+chunkX*stepX-20*radius,y0-(chunkY+chunkYStep)*stepY-20*radius)
# 				br = pair[double,double](x0+(chunkX+chunkXStep)*stepX+20*radius,y0-chunkY*stepY+20*radius)
# # 				self.__grid.set_corners(tl,br)
# 				for i in prange(chunkX,self._noGILMin(chunkX+chunkXStep,resx),nogil=True,schedule='guided',num_threads=self.core_count):
# # 				for i in range(chunkX,self._noGILMin(chunkX+chunkXStep,resx)):
# 					for j in range(chunkY,self._noGILMin(chunkY+chunkYStep,resy)):
# 						# print(str(x0+i*stepX)+","+str(y0-stepY*j))
# 						retArr[i,j] = (<double> self.query_data_length(x0+i*stepX,y0-stepY*j,radius))/trueLuminosity
# 		return retArr
