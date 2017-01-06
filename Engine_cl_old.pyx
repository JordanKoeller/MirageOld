# cython: profile=True


import numpy as np
cimport numpy as np
from WrappedTree import WrappedTree
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

cdef class Engine_cl:

	def __init__(self,quasar,galaxy,configs):
		self.quasar = quasar
		self.galaxy = galaxy
		self.configs = configs
		self.preCalculating = False
		self.calculating = False
		self.time = 0.0
		self.dL = self.galaxy.angDiamDist.to("lyr") #ADD
		self.dS = self.quasar.angDiamDist.to("lyr")
		self.dLS = cosmo.angular_diameter_distance_z1z2(self.galaxy.redShift,self.quasar.redShift).to('lyr')
		self.einsteinRadius = math.sqrt(const.G.value * galaxy.mass.to("kg").value * 4 * (self.dLS.to("m").value/(self.dL.to("m").value*self.dS.to("m").value)) / (const.c.value*const.c.value))


	cdef ray_trace_gpu(self):
		os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
		os.environ['PYOPENCL_CTX'] = '0:1'
		cdef int height = self.configs.canvasDim.y
		cdef int width = self.configs.canvasDim.x
		cdef double dTheta = self.configs.dTheta
		cdef np.ndarray result_nparray_x = np.ndarray((width,height), dtype = np.float32)
		cdef np.ndarray result_nparray_y = np.ndarray((width,height), dtype = np.float32)
		# cdef np.ndarray pixelsArray = np.ndarray((width,height), dtype = np.dtype([
		# 	('x', np.float32), 
		# 	('y', np.float32)]))
		stars_nparray = self.galaxy.getStarArray()
		# print(pixelsArray)

		# create a context and a job queue
		context = cl.create_some_context()
		queue = cl.CommandQueue(context)

		# create buffers to send to device
		mf = cl.mem_flags
		dtype = stars_nparray.dtype
		# pixel_dtype = pixelsArray.dtype
		# pixel_dtype, c_pixel_decl = cl.tools.match_dtype_to_c_struct(context.devices[0],'pixel_struct',dtype)
		dtype, c_decl = cl.tools.match_dtype_to_c_struct(context.devices[0],'lenser_struct',dtype)
		cl.tools.get_or_register_dtype('lenser_struct',stars_nparray.dtype)
		# cl.tools.get_or_register_dtype('pixel_struct',pixelsArray.dtype)
		#input buffers
		stars_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf = stars_nparray)

		#output buffers
		result_buffer_x = cl.Buffer(context, mf.READ_WRITE, result_nparray_x.nbytes)
		result_buffer_y = cl.Buffer(context, mf.READ_WRITE, result_nparray_y.nbytes)
		# pixels_buffer = cl.Buffer(context, mf.READ_WRITE, pixelsArray.nbytes)

		# read and compile opencl kernel
		prg = cl.Program(context,c_decl + open('engine_helper.cl').read()).build(['-cl-fp32-correctly-rounded-divide-sqrt'])
		prg.ray_trace(queue,(width,height),None,
			stars_buffer,
			np.int32(self.galaxy.numStars),
			np.float32((4*const.G/(const.c*const.c)).to("lyr/solMass").value),
			np.float32(self.dL.value),
			np.float32(self.dLS.value),
			np.int32(width), np.int32(height),
			np.float32(self.configs.dTheta),
			# pixels_buffer)
			result_buffer_x,
			result_buffer_y)

		# clean up GPU memory while copying data back into RAM
		cl.enqueue_copy(queue,result_nparray_x,result_buffer_x).wait()
		cl.enqueue_copy(queue,result_nparray_y,result_buffer_y).wait()
		# cl.enqueue_copy(queue,pixelsArray,pixels_buffer).wait()
		# print(pixelsArray)
		# return pixelsArray
		return (result_nparray_x,result_nparray_y)


	cpdef reConfigure(self,configs):
		begin = time.clock()
		self.preCalculating = True
		self.configs = configs
		finalData = self.ray_trace_gpu()
		print("time ray tracing = " + str(time.clock() - begin) + " seconds.")
		begin = time.clock()
		self.tree = WrappedTree()
		self.tree.setDataFromNumpies(finalData)
		print("time building tree = " + str(time.clock() - begin) + " seconds.")
		self.preCalculating = False


	cpdef start(self, canvas):
		# periodogram_opencl()
		self.reConfigure(self.configs)
		self.calculating = True
		width = self.configs.canvasDim.x
		height = self.configs.canvasDim.y
		if not self.preCalculating:
			self.galaxy.draw(canvas,self.configs.dTheta)
			while self.calculating:
				self.drawFrame(canvas)
				self.quasar.draw(canvas,self.configs.dTheta)
				# print("New frame")


	cpdef getPixelCount(self,position):
		self.quasar.setPos(position)
		ret = len(self.tree.getInBall(self.quasar.observedPosition,self.quasar.radius))
		return ret


	cpdef restart(self):
		self.calculating = False
		self.time = 0.0


	cpdef pause(self):
		self.calculating = False
		

	cdef drawFrame(self,canvas):
		width = self.configs.canvasDim.x
		height = self.configs.canvasDim.y
		dt = self.configs.dt
		coloredPixels = np.full(shape=(width,height),fill_value = 0, dtype = np.int)
		self.quasar.setTime(self.time)
		ret = self.tree.getInBall(self.quasar.observedPosition,self.quasar.radius.value)
		# print(len(ret))
		for pixel in ret:
			coloredPixels[pixel[0],pixel[1]] = 2
		canvas.plotArray(coloredPixels)
		self.time += dt
		

	cdef calcDeflections(self):
		pass


	cdef queryTree(self,position):
		pass

