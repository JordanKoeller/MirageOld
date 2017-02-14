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



cdef packed struct lenser_struct:
	np.int32_t lenserType
	np.float64_t mass
	np.float64_t x
	np.float64_t y
	np.float64_t radius


cdef class Engine_cl:

	def __init__(self,quasar,galaxy,configs, auto_configure = True):
		self.__quasar = quasar
		self.__galaxy = galaxy
		self.__configs = configs
		self.__preCalculating = False
		self.__needsReconfiguring = True
		self.time = 0.0
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))#*206264806247.09637
		self.__galaxy.generateStars(self.einsteinRadius, self.configs)
		# self.__trueLuminosity = math.pi * (self.__quasar.radius.value/self.__configs.dTheta)**2
		self.img = QtGui.QImage(self.__configs.canvasDim,self.__configs.canvasDim, QtGui.QImage.Format_Indexed8)
		self.__imgColors = [QtGui.qRgb(0,0,0),QtGui.qRgb(255,255,0),QtGui.qRgb(255,255,255),QtGui.qRgb(50,101,255),QtGui.qRgb(244,191,66)]
		self.img.setColorTable(self.__imgColors)
		self.img.fill(0)
		if auto_configure:
			self.reconfigure()

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

	@property
	def needsReconfiguring(self):
		return self.__needsReconfiguring

	def ray_trace(self, use_GPU = False):
		return self.ray_trace_gpu(False)

	def setShift(self,newConfigs,enabled, theta = math.pi):
		newConfigs.setShift(enabled,self.einsteinRadius, theta = math.pi)
		if enabled:
			# self.__galaxy.generateStars
			newConfigs.displayQuasar = False
			newConfigs.displayGalaxy = False
		##### TODO #####


	cdef ray_trace_gpu(self,use_GPU):
		begin = time.clock()
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		if use_GPU:
			os.environ['PYOPENCL_CTX'] = '0:1'
		else:
			os.environ['PYOPENCL_CTX'] = '0:0'
		cdef int height = self.__configs.canvasDim
		cdef int width = self.__configs.canvasDim
		cdef np.float64_t dTheta = self.__configs.dTheta
		cdef np.ndarray result_nparray_x = np.ndarray((width,height), dtype = np.float64)
		cdef np.ndarray result_nparray_y = np.ndarray((width,height), dtype = np.float64)
		stars_nparray_mass, stars_nparray_x, stars_nparray_y = self.__galaxy.getStarArray()

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

		# create buffers to send to device
		mf = cl.mem_flags
		# dtype = stars_nparray.dtype

		# dtype, c_decl = cl.tools.match_dtype_to_c_struct(context.devices[0],'lenser_struct',dtype)
		# cl.tools.get_or_register_dtype('lenser_struct',stars_nparray.dtype)

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
			np.float64((4*const.G/(const.c*const.c)).to("lyr/solMass").value), #np.float64 (0.12881055652653947), #
			np.float64(4*math.pi*(const.c**-2).to('s2/km2').value),#np.float64 (28.83988945290979), #
			# np.float64(math.sin(2*self.galaxy.shear.angle.value+math.pi/2)),
			# np.float64(-math.cos(2*self.galaxy.shear.angle.value+math.pi/2)),
			np.float64(self.galaxy.shear.magnitude),
			np.float64(self.galaxy.shear.angle.value),
			np.float64(self.galaxy.velocityDispersion),
			np.float64(self.galaxy.angDiamDist.value),
			np.float64(self.quasar.angDiamDist.value),
			np.float64(self.__dLS.value),
			np.int32(width),
			np.int32(height),
			np.float64(self.configs.dTheta),
			np.float64(self.galaxy.position.to('rad').x),
			np.float64(self.galaxy.position.y),
			result_buffer_x,
			result_buffer_y)

		# clean up GPU memory while copying data back into RAM
		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x)
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y)
		# print(result_nparray_x)
		# print(result_nparray_y)
		print("Time Ray-Tracing = " + str(time.clock()-begin))
		return (result_nparray_x,result_nparray_y)

	@cython.boundscheck(False) # turn off bounds-checking for entire function
	@cython.wraparound(False)  # turn off negative index wrapping for entire function
	cdef ray_trace_cCode(self):
		cdef int height = self.__configs.canvasDim
		cdef int width = self.__configs.canvasDim
		cdef np.float64_t dTheta = self.__configs.dTheta
		cdef np.ndarray[dtype=np.float64_t, ndim=2, mode="c"] result_nparray_x = np.ndarray((width,height), dtype = np.float64)
		cdef np.ndarray[dtype=np.float64_t, ndim=2, mode="c"] result_nparray_y = np.ndarray((width,height), dtype = np.float64)
		result_nparray_x = np.ascontiguousarray(result_nparray_x)
		result_nparray_y = np.ascontiguousarray(result_nparray_y)
		cdef np.ndarray[dtype=lenser_struct, ndim=1, mode="c"] stars_nparray = self.__galaxy.getStarArray()
		stars_nparray = np.ascontiguousarray(stars_nparray)
		cdef lenser_struct [:] stars_buffer = stars_nparray
		engineHelper.ray_trace(&stars_nparray[0],
			np.int32(self.__galaxy.numStars),
			np.float64((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
			np.float64(4*math.pi*(const.c**-2).to('s2/km2').value),
			np.float64(self.galaxy.angDiamDist.value),
			np.float64(self.quasar.angDiamDist.value),
			np.float64(self.__dLS.value),
			np.int32(width),
			np.int32(height),
			np.float64(self.configs.dTheta),
			np.float64(self.configs.frameShift.x),
			np.float64(self.configs.frameShift.y),
			&result_nparray_x[0,0],
			&result_nparray_y[0,0])
		return (result_nparray_x,result_nparray_y)

	@cython.boundscheck(False) # turn off bounds-checking for entire function
	@cython.wraparound(False)  # turn off negative index wrapping for entire function
	cdef ray_trace_cython(self):
		cdef np.float64_t begin = time.clock()
		cdef int height = self.__configs.canvasDim
		cdef int width = self.__configs.canvasDim
		cdef np.float64_t dTheta = self.__configs.dTheta
		cdef np.ndarray[dtype=np.float64_t, ndim=2] result_nparray_x = np.ndarray((width,height), dtype = np.float64)
		cdef np.ndarray[dtype=np.float64_t, ndim=2] result_nparray_y = np.ndarray((width,height), dtype = np.float64)
		cdef np.ndarray[dtype=lenser_struct, ndim=1] stars_nparray = self.__galaxy.getStarArray()
		cdef int numStars = len(stars_nparray)
		cdef np.float64_t point_constant = (4*const.G/(const.c*const.c)).to("lyr/solMass").value
		cdef np.float64_t sis_constant = 4*math.pi*(const.c**-2).to('s2/km2').value
		cdef np.float64_t velocityDispersion = self.galaxy.velocityDispersion.value
		cdef np.float64_t dL = self.galaxy.angDiamDist.value
		cdef np.float64_t dLS = self.__dLS.value
		cdef np.float64_t dS = self.quasar.angDiamDist.value
		cdef np.float64_t galaxyCenterX = self.galaxy.position.x
		cdef np.float64_t galaxyCenterY = self.galaxy.position.y
		cdef np.float64_t shearMag = self.galaxy.shear.magnitude
		cdef np.float64_t shearAngle = self.galaxy.shear.angle.value
		cdef np.float64_t M_PI_2 = math.pi//2
		cdef np.float64_t dRX, dRY, incidentAngleX, incidentAngleY, r
		cdef unsigned int i, j, star
		for i in range(0,width):
			for j in range(0,height):
				incidentAngleX = (((i - width//2)*dTheta) + galaxyCenterX) or 0.000000000000001
				incidentAngleY = (((j - height//2)*dTheta) + galaxyCenterY) or 0.000000000000001
				result_nparray_x[i][j] = 0.0
				result_nparray_y[i][j] = 0.0
				for star in range(0,numStars-2):
					dRX = (stars_nparray[star].x - incidentAngleX)*dL
					dRY = (stars_nparray[star].y - incidentAngleY)*dL
					r = sqrt(dRX*dRX + dRY*dRY)		
					result_nparray_x[i][j] += dRX*stars_nparray[star].mass*point_constant//(r*r)
					result_nparray_y[i][j] += dRY*stars_nparray[star].mass*point_constant/(r*r)
				dRX = galaxyCenterX - incidentAngleX
				dRY = galaxyCenterY - incidentAngleY
				r = sqrt(dRX*dRX + dRY*dRY)
				result_nparray_x[i][j] += velocityDispersion*velocityDispersion*dRX*sis_constant#//r
				result_nparray_y[i][j] += velocityDispersion*velocityDispersion*dRY*sis_constant#//r
				dRX = dRX // r 
				dRY = dRY // r
				result_nparray_x[i][j] = result_nparray_x[i][j]+ shearMag*r*cos(2*(shearAngle+M_PI_2) - atan2(dRY,dRX))
				result_nparray_y[i][j] = result_nparray_y[i][j]+shearMag*r*sin(2*(shearAngle+M_PI_2) - atan2(dRY,dRX))
				result_nparray_x[i][j] = (incidentAngleX*dL + (incidentAngleX+result_nparray_x[i][j])*dLS)//dS
				result_nparray_y[i][j] = (incidentAngleY*dL + (incidentAngleY+result_nparray_y[i][j])*dLS)//dS
		print(time.clock() - begin)
		# print(result_buffer)
		return (result_nparray_x,result_nparray_y)

	cpdef reconfigure(self):
		if self.__needsReconfiguring:
			self.__galaxy.generateStars(self.einsteinRadius,self.configs)
			begin = time.clock()
			self.__preCalculating = True
			self.__tree = WrappedTree()
			finalData = self.ray_trace(use_GPU = True)
			self.__tree.setDataFromNumpies(finalData)
			print("Time calculating = " + str(time.clock() - begin) + " seconds.")
			self.__preCalculating = False
			self.__needsReconfiguring = False


	cpdef getMagnification(self):
		cdef a = np.float64 (self.__trueLuminosity)
		cdef b = np.float64 (self.__tree.query_point_count(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius.value))
		return b/a

	cdef buildTree(self, data):
		xvals = data[0]
		yvals = data[1]
		cdef int width = self.__configs.canvasDim
		cdef int height = self.__configs.canvasDim
		cdef np.float64_t __dS = self.quasar.angDiamDist.value
		cdef int i = 0
		cdef int j = 0
		for i in range(width):
			for j in range(height):
				self.__tree.insert(i,j,xvals[i,j],yvals[i,j])
		

	cpdef getFrame(self):
		# print("New Frame")
		if self.__needsReconfiguring:
			self.reconfigure()
		cdef int width = self.__configs.canvasDim
		cdef int height = self.__configs.canvasDim
		cdef np.float64_t dt = self.__configs.dt
		self.__quasar.setTime(self.time)
		ret = self.__tree.query_point(self.__quasar.observedPosition.x,self.__quasar.observedPosition.y,self.__quasar.radius.value)
		self.img.fill(0)
		if self.configs.displayQuasar:
			self.quasar.draw(self.img,self.configs)
		if self.configs.displayGalaxy:
			self.galaxy.draw(self.img,self.configs)
		for pixel in ret:
			# self.img.setPixel(pixel.real,pixel.imag,1)
			self.img.setPixel(pixel[0],pixel[1],1)
		return self.img

		

	cdef calcDeflections(self):
		pass


	cdef queryTree(self,position):
		pass


	def updateQuasar(self,quasar = None,redshift = None,position = None,radius = None,velocity = None, auto_configure = True):
		newQ = quasar or self.__quasar
		newQ.update(redshift = redshift,position = position,radius = radius,velocity = velocity)
		if self.quasar.redshift != newQ.redshift:
			self.__needsReconfiguring = True
			self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,newQ.redshift).to('lyr')
			self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))#*206264806247.09637
		# self.__trueLuminosity = math.pi * (newQ.radius.value/self.__configs.dTheta)**2
		self.__quasar = newQ
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateGalaxy(self,galaxy = None ,redshift = None, velocityDispersion = None, radius = None, numStars = None, auto_configure = True, center = zeroVector):
		if galaxy != None:
			if galaxy.redshift != self.galaxy.redshift or galaxy.velocityDispersion != self.galaxy.velocityDispersion  or galaxy.shear.magnitude != self.galaxy.shear.magnitude or galaxy.shear.angle != self.galaxy.shear.angle:# or galaxy.center != self.galaxy.center:
				self.__needsReconfiguring = True
		if galaxy is None:
			self.__needsReconfiguring = True
		self.__galaxy = galaxy or self.__galaxy
		self.__galaxy.update(redshift = redshift,velocityDispersion = velocityDispersion,numStars = numStars, stars = self.__galaxy.stars)
		self.__dLS = cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')
		self.__einsteinRadius = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))#*206264806247.09637
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()

	def updateConfigs(self,configs = None, dt = None, dTheta = None, canvasDim = None, auto_configure = True, frameRate = None, displayGalaxy = None, displayQuasar = None,colorQuasar = None, shiftGalacticCenter = None):
		#Need to redo this so that upon rescaling, centers around screeen
		newConfigs = configs or self.__configs
		newConfigs.dt = dt or newConfigs.dt
		newConfigs.dTheta = dTheta or newConfigs.dTheta
		newConfigs.canvasDim = canvasDim or newConfigs.canvasDim
		if colorQuasar is not None:
			newConfigs.colorQuasar = colorQuasar
		if shiftGalacticCenter is not None:
			newConfigs.shiftGalaxy = shiftGalacticCenter
		if displayGalaxy is not None:
			newConfigs.displayGalaxy = displayGalaxy
		if displayQuasar is not None:
			newConfigs.displayQuasar = displayQuasar
		if newConfigs.dTheta - self.__configs.dTheta != 0:
			pass
			# self.__trueLuminosity = math.pi * (self.quasar.radius.value/newConfigs.dTheta)**2
			# self.__needsReconfiguring = True
		if newConfigs.canvasDim - self.__configs.canvasDim != zeroVector:
			##### ERROR HERE causing it to continually recalculate #####
			# self.__needsReconfiguring = True
			self.img = QtGui.QImage(self.__configs.canvasDim,self.__configs.canvasDim, QtGui.QImage.Format_Indexed8)
			self.img.setColorTable(self.__imgColors)
			self.img.fill(0)
		if shiftGalacticCenter is not None:
			if shiftGalacticCenter:
				# self.__needsReconfiguring = True
				# self.setShift(newConfigs,shiftGalacticCenter, theta = math.pi)
				newConfigs.dTheta = 100  #Need to fix
				# self.__trueLuminosity = math.pi * (self.quasar.radius.value/newConfigs.dTheta)**2
			else:
				pass
				# self.__needsReconfiguring = True
		self.__configs = newConfigs
		if auto_configure and self.__needsReconfiguring:
			self.reconfigure()


