# distutils: language=c++
# cython: profile=True
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
from Parameters import Parameters
from matplotlib import pyplot as pl
from scipy import interpolate


cdef class Engine_cl:

	def __init__(self,parameters = Parameters()):
		self.__parameters = parameters
		self.__preCalculating = False
		self.time = 0.0
		self.__trueLuminosity = math.pi * (self.__parameters.quasar.radius.value/self.__parameters.dTheta)**2
		self.img = QtGui.QImage(800,800, QtGui.QImage.Format_Indexed8)
		self.__imgColors = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66)]
		self.img.setColorTable(self.__imgColors)
		self.img.fill(0)

	@property
	def parameters(self):
		return self.__parameters

	def ray_trace(self, use_GPU = False):
		return self.ray_trace_gpu(False)

	def drawEinsteinRadius(self,canvas,radius,centerx,centery):
		cdef int x0, y0
		x0 = centerx
		y0 = centery
		cdef int x = abs(radius/self.__parameters.dTheta)
		cdef int y = 0
		cdef int err = 0
		while x >= y:
			canvas.setPixel(x0 + x, y0 + y,1)
			canvas.setPixel(x0 + y, y0 + x,1)
			canvas.setPixel(x0 - y, y0 + x,1)
			canvas.setPixel(x0 - x, y0 + y,1)
			canvas.setPixel(x0 - x, y0 - y,1)
			canvas.setPixel(x0 - y, y0 - x,1)
			canvas.setPixel(x0 + y, y0 - x,1)
			canvas.setPixel(x0 + x, y0 - y,1)
			if err <= 0:
				y += 1
				err += 2*y + 1
			if err > 0:
				x -= 1
				err -= 2*x + 1

	cdef ray_trace_gpu(self,use_GPU):
		# print(self.__parameters)
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		if use_GPU:
			os.environ['PYOPENCL_CTX'] = '0:1'
		else:
			os.environ['PYOPENCL_CTX'] = '0:0'
		cdef int height = self.__parameters.canvasDim
		cdef int width = self.__parameters.canvasDim
		cdef np.float64_t dTheta = self.__parameters.dTheta
		cdef np.ndarray result_nparray_x = np.ndarray((width,height), dtype = np.float64)
		cdef np.ndarray result_nparray_y = np.ndarray((width,height), dtype = np.float64)
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__parameters.galaxy.getStarArray()

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

		# create buffers to send to device
		mf = cl.mem_flags		
		#input buffers
		stars_buffer_mass = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray_mass)
		stars_buffer_x = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray_x)
		stars_buffer_y = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray_y)
		#output buffers
		result_buffer_x = cl.Buffer(context, mf.READ_WRITE, result_nparray_x.nbytes)
		result_buffer_y = cl.Buffer(context, mf.READ_WRITE, result_nparray_y.nbytes)

		# read and compile opencl kernel
		prg = cl.Program(context, open('engine_helper.cl').read()).build()
		prg.ray_trace(queue,(width,height),None,
			stars_buffer_mass,
			stars_buffer_x,
			stars_buffer_y,
			np.int32(len(stars_nparray_x)),
			np.float64((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
			np.float64(4*math.pi*(const.c**-2).to('s2/km2').value),
			np.float64(self.__parameters.galaxy.shear.magnitude),
			np.float64(self.__parameters.galaxy.shear.angle.value),
			np.float64(self.__parameters.galaxy.velocityDispersion.value),
			np.float64(self.__parameters.galaxy.angDiamDist.value),
			np.float64(self.__parameters.quasar.angDiamDist.value),
			np.float64(self.__parameters.dLS.value),
			np.int32(width),
			np.int32(height),
			np.float64(self.__parameters.dTheta),
			np.float64(self.__parameters.galaxy.position.to('rad').x),
			np.float64(self.__parameters.galaxy.position.y),
			result_buffer_x,
			result_buffer_y)

		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x)
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y)
		print("Time Ray-Tracing = " + str(time.clock()-begin))
		return (result_nparray_x,result_nparray_y)

	cpdef reconfigure(self):
		begin = time.clock()
		self.__preCalculating = True
		self.img = QtGui.QImage(self.__parameters.canvasDim,self.__parameters.canvasDim, QtGui.QImage.Format_Indexed8)
		self.__imgColors = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66)]
		self.img.setColorTable(self.__imgColors)
		self.img.fill(0)
		self.__tree = WrappedTree()
		finalData = self.ray_trace(use_GPU = True)
		self.__tree.setDataFromNumpies(finalData)
		self.__preCalculating = False
		print("Time calculating = " + str(time.clock() - begin) + " seconds.")

	# def calcMassOnScreen(self):
	# 	return u.Quantity(2*(self.__parameters.galaxy.velocityDispersion.value**2)*(self.__parameters.dTheta**2)*(self.__parameters.galaxy.angDiamDist.value**2)/(const.G.to('lyr3/(solMass s2)').value*2*math.pi*self.__calcER()),'solMass')

	def calTheta(self):
		k = (4*math.pi*(const.c**-2).to('s2/km2').value * self.__parameters.dLS.value/self.__parameters.quasar.angDiamDist.value* self.__parameters.galaxy.velocityDispersion.value * self.__parameters.galaxy.velocityDispersion.value)+(self.__parameters.quasar.position-self.__parameters.galaxy.position).magnitude()
		theta = (k/(1-(self.__parameters.dLS.value/self.__parameters.quasar.angDiamDist.value)*self.__parameters.galaxy.shearMag))
		theta2 = (k/(1+(self.__parameters.dLS.value/self.__parameters.quasar.angDiamDist.value)*self.__parameters.galaxy.shearMag))
		return (theta,theta2)

	cpdef getMagnification(self):
		cdef a = np.float64 (self.__trueLuminosity)
		cdef b = np.float64 (self.__tree.query_point_count(self.__parameters.quasar.observedPosition.x,self.__parameters.quasar.observedPosition.y,self.__parameters.quasar.radius.value))
		return b/a

	cpdef getFrame(self):
		cdef int width = self.__parameters.canvasDim
		cdef int height = self.__parameters.canvasDim
		cdef np.float64_t dt = self.__parameters.dt
		self.__parameters.setTime(self.time)
		ret = self.__tree.query_point(self.__parameters.quasar.observedPosition.x,self.__parameters.quasar.observedPosition.y,self.__parameters.quasar.radius.value)
		self.img.fill(0)
		if self.__parameters.displayQuasar:
			self.__parameters.quasar.draw(self.img,self.__parameters)
		if self.__parameters.displayStars:
			imgs = self.calTheta()
			self.__parameters.galaxy.draw(self.img,self.__parameters, self.__parameters.displayGalaxy)
			# self.drawEinsteinRadius(self.img,imgs[0],400+self.__parameters.galaxy.position.x/self.__parameters.dTheta,400+self.__parameters.galaxy.position.y/self.__parameters.dTheta)
			# self.drawEinsteinRadius(self.img,imgs[1],400+self.__parameters.galaxy.position.x/self.__parameters.dTheta,400+self.__parameters.galaxy.position.y/self.__parameters.dTheta)
		for pixel in ret:
			self.img.setPixel(pixel[0],pixel[1],1)
		return (self.img,self.__parameters.dt)

	cdef cythonMakeLightCurve(self,mmin, mmax,resolution,canvas, progressBar, smoothing):
		begin = time.clock()
		# progressBar.setMinimum(0)
		# progressBar.setMaximum(int(resolution))
		cdef int counter = 0
		stepX = (mmax.x - mmin.x)/resolution
		stepY = (mmax.y - mmin.y)/resolution
		yAxis= np.arange(0,resolution)
		xVals = np.arange(0,1,1/resolution)
		cdef int i = 0
		cdef double radius = self.__parameters.quasar.radius.value
		print("radius = "+str(radius))
		for i in range(0,resolution):
			x = mmin.x + stepX*i
			y = mmin.y + stepY*i
			print(str(xVals[i])+" :: " + str(x)+","+str(y))
			yAxis[i] = self.__tree.query_point_count(x,y,radius)
			counter += 1
			# progressBar.setValue(counter)
		print("clocked at = " + str(time.clock() - begin) + " seconds")
		# print(xVals)
		if smoothing:
			xNew = np.arange(0,1,1/(resolution*10))
			yNew = np.empty_like(xNew)
			tck = interpolate.splrep(xVals,yAxis, s = 0)
			yNew = interpolate.splev(xNew, tck, der=0)
			# pl.plot(xNew,yNew)
			return (xNew,yNew)
		else:
			return (xVals,yAxis)
			# pl.plot(xVals,yAxis)
			# pl.show()
		# canvas.plot.legend()
		# canvas.plot.xlabel("Distance of quasar from galactic center (theta_E)")
		# canvas.plot.ylabel("Magnification Coefficient")
		# canvas.plot.show()

	def makeLightCurve(self,mmin,mmax,resolution=200,canvas = None, progressBar = None, smoothing = False):
		return self.cythonMakeLightCurve(mmin,mmax,resolution,canvas,progressBar,smoothing)


	def updateParameters(self,parameters):
		# print(parameters)
		if self.__parameters is None:
			# print("is none")
			self.__parameters = parameters
			self.reconfigure()
		elif not self.__parameters.isSimilar(parameters):
			# print("is not similar")
			self.__parameters = parameters
			self.reconfigure()
			self.__parameters.generateStars()
		else:
			# print("is Similar")
			parameters.setStars(self.__parameters.stars)
			self.__parameters = parameters





