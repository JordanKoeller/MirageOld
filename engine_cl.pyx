# distutils: language=c++
# cython: profile=True

import numpy as np
cimport numpy as np
from WrappedTree_old import WrappedTree
from stellar import Galaxy
from stellar import Quasar
from Configs import Configs 
from astropy.cosmology import WMAP7 as cosmo
from Vector2D import Vector2D
import time
from astropy import constants as const
import math
import pyopencl as cl
import pyopencl.tools
import os
from SpatialTree cimport SpatialTree, Pixel
from libcpp.vector cimport vector
import random
from PyQt5 import QtGui


cdef class Engine_cl:

	def __init__(self,quasar,galaxy,configs, auto_configure = True):
		self.__quasar = quasar
		self.__galaxy = galaxy
		self.__configs = configs
		self.__preCalculating = False
		self.__calculating = False
		self.__needsReconfiguring = True
		self.time = 0.0
		self.dL = self.__galaxy.angDiamDist #ADD
		self.dS = self.__quasar.angDiamDist
		self.dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr').value
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.dLS/self.dS /((const.c**2).to('km2/s2').value)
		self.__galaxy.generateStars(self.einsteinRadius)
		self.trueLuminosity = math.pi * (self.__quasar.radius/self.__configs.dTheta)**2
		if auto_configure:
			self.reConfigure()

	@property
	def configs(self):
		return self.__configs

	@property
	def galaxy(self):
		return self.__galaxy

	@property
	def quasar(self):
		return self.__quasar

	@property
	def einsteinRadius(self):
		return self.__einsteinRadius

	cdef ray_trace_gpu(self):
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		os.environ['PYOPENCL_CTX'] = '0:1'
		cdef int height = self.__configs.canvasDim.y
		cdef int width = self.__configs.canvasDim.x
		cdef double dTheta = self.__configs.dTheta
		cdef np.ndarray result_nparray_x = np.ndarray((width,height), dtype = np.float32)
		cdef np.ndarray result_nparray_y = np.ndarray((width,height), dtype = np.float32)
		stars_nparray = self.__galaxy.getStarArray()

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

 
		# create buffers to send to device
		mf = cl.mem_flags
		dtype = stars_nparray.dtype

		dtype, c_decl = cl.tools.match_dtype_to_c_struct(context.devices[0],'lenser_struct',dtype)
		cl.tools.get_or_register_dtype('lenser_struct',stars_nparray.dtype)

		#input buffers
		stars_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray)

		#output buffers
		result_buffer_x = cl.Buffer(context, mf.READ_WRITE, result_nparray_x.nbytes)
		result_buffer_y = cl.Buffer(context, mf.READ_WRITE, result_nparray_y.nbytes)

		# read and compile opencl kernel
		prg = cl.Program(context,c_decl + open('engine_helper.cl').read()).build(['-cl-fp32-correctly-rounded-divide-sqrt'])
		prg.ray_trace(queue,(width,height),None,
			stars_buffer,
			np.int32(self.__galaxy.numStars),
			np.float32((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
			np.float32(4*math.pi*(const.c**-2).to('s2/km2').value),
			np.float32(self.dL),
			np.float32(self.dS),
			np.float32(self.dLS),
			np.int32(width),
			np.int32(height),
			np.float32(self.__configs.dTheta),
			result_buffer_x,
			result_buffer_y)

		# clean up GPU memory while copying data back into RAM
		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x).wait()
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y).wait()

		return (result_nparray_x,result_nparray_y)



	cpdef reConfigure(self):
		if self.__needsReconfiguring:
			print('Initializing. Please wait.')
			begin = time.clock()
			self.__preCalculating = True
			self.tree = WrappedTree()
			finalData = self.ray_trace_gpu()
			print("time ray-tracing tree = " + str(time.clock() - begin) + " seconds.")
			begin = time.clock()
			# self.buildTree(finalData)
			self.tree.setDataFromNumpies(finalData)
			print("time building tree = " + str(time.clock() - begin) + " seconds.")
			self.__preCalculating = False
			self.__needsReconfiguring = False


	cpdef start(self, canvas):
		self.img = QtGui.QImage(self.__configs.canvasDim.x,self.__configs.canvasDim.y, QtGui.QImage.Format_Indexed8)
		self.img.setColorTable([QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0)])
		self.img.fill(0)
		canvas.setPixmap(QtGui.QPixmap.fromImage(self.img))
		# timeSum = 0.0
		if self.__needsReconfiguring:
			self.reConfigure()
		self.__calculating = True
		width = self.__configs.canvasDim.x
		height = self.__configs.canvasDim.y
		if not self.__preCalculating:
			# begin = time.clock()
			# counter = 0
			while self.__calculating:
				# timeSum += self.drawFrame(canvas)
				self.drawFrame(canvas)
				# counter += 1
				# if counter % 25 is 0:
				# 	end = time.clock()
				# 	print('')
				# 	print("Next Printout")
				# 	print("Frame Rate = " + str(1/((end-begin)/25)) + " FPS")
				# 	print("Tree Rate = " + str(1/((end-begin-timeSum)/25)) + " FPS")
				# 	timeSum = 0.0
				# 	begin = time.clock()



	cpdef getMagnification(self):
		cdef a = np.double(self.trueLuminosity)
		cdef b = np.double(self.tree.query_point_count(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius))
		# print("(a,b) = (" + str(a) + "," + str(b) + ")")
		return b/a
		# return posLuminosity/self.trueLuminosity

	cdef buildTree(self, data):
		xvals = data[0]
		yvals = data[1]
		cdef int width = self.__configs.canvasDim.x
		cdef int height = self.__configs.canvasDim.y
		cdef double dS = self.dS
		cdef int i = 0
		cdef int j = 0
		for i in range(width):
			for j in range(height):
				self.tree.insert(i,j,xvals[i,j],yvals[i,j])

	cpdef restart(self):
		self.__calculating = False
		self.time = 0.0


	cpdef pause(self):
		self.__calculating = False
		

	cdef drawFrame(self,canvas):
		cdef int width = self.__configs.canvasDim.x
		cdef int height = self.__configs.canvasDim.y
		cdef double dt = self.__configs.dt
		self.__quasar.setTime(self.time)
		ret = self.tree.query_point(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius)
		begin = time.clock()
		self.img.fill(0)
		for pixel in ret:
			self.img.setPixel(pixel[1],pixel[0],1)
		canvas.pixmap().convertFromImage(self.img)
		canvas.update()
		# canvas.setPixmap(QtGui.QPixmap.fromImage(self.img))
		# canvas.plotArray(coloredPixels)
		self.time += dt
		return time.clock() - begin
		

	cdef calcDeflections(self):
		pass


	cdef queryTree(self,position):
		pass

	def updateQuasar(self,quasar = None,redshift = None,position = None,radius = None,velocity = None, auto_reconfigure = True):
		newQ = quasar or self.__quasar
		newQ.update(redshift,position,radius,velocity)
		if self.__quasar.redshift != newQ.redshift:
			self.__needsReconfiguring = True
			self.dS = newQ.angDiamDist
			self.dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,newQ.redshift).to('lyr').value
			self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.dLS/self.dS /((const.c**2).to('km2/s2').value)
		self.trueLuminosity = math.pi * (newQ.radius/self.__configs.dTheta)**2
		self.__quasar = newQ
		if auto_reconfigure and self.__needsReconfiguring:
			self.reConfigure()

	def updateGalaxy(self,galaxy = None ,redshift = None, velocityDispersion = None, radius = None, numStars = None, auto_reconfigure = True):
		self.__needsReconfiguring = True
		self.__galaxy = galaxy or self.__galaxy
		self.__galaxy.update(redshift,velocityDispersion,radius,numStars)
		self.dL = self.__galaxy.angDiamDist #ADD
		self.dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr').value
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.dLS/self.dS /((const.c**2).to('km2/s2').value)
		self.__galaxy.generateStars(self.einsteinRadius)
		if auto_reconfigure and self.__needsReconfiguring:
			self.reConfigure()

	def updateConfigs(self,configs = None, dt = None, dTheta = None, canvasDim = None, auto_reconfigure = True):
		newConfigs = configs or self.__configs
		newConfigs.dt = dt or self.__configs.dt
		newConfigs.dTheta = dTheta or self.__configs.dTheta
		newConfigs.canvasDim = canvasDim or self.__configs.canvasDim
		if newConfigs.dTheta != self.__configs.dTheta:
			self.trueLuminosity = math.pi * (self.quasar.radius/self.__configs.dTheta)**2
			self.__needsReconfiguring = True
		if newConfigs.canvasDim != self.__configs.canvasDim:
			self.__needsReconfiguring = True
		if auto_reconfigure and self.__needsReconfiguring:
			self.reConfigure()

