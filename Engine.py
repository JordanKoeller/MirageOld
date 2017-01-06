import numpy as np
from WrappedTree import WrappedTree
from stellar import Galaxy
from stellar import Quasar
from Configs import Configs 
from astropy.cosmology import WMAP7 as cosmo
from Vector2D import Vector2D
import time
from astropy import constants as const
import math
from numba import jit
class EngineOld(object):


	def __init__(self,quasar,galaxy,configs):
		self.quasar = quasar
		self.galaxy = galaxy
		self.configs = configs
		self.preCalculating = False
		self.calculating = False
		self.time = 0.0
		self.dL = cosmo.angular_diameter_distance(self.galaxy.redShift).to('lyr').value #ADD
		self.dS = cosmo.angular_diameter_distance(self.quasar.redShift).to('lyr').value
		self.dLS = cosmo.angular_diameter_distance_z1z2(self.galaxy.redShift,self.quasar.redShift).to('lyr').value
		# self.einsteinRadius = math.sqrt(const.G.value * galaxy.mass * 4 * (self.dLS/(self.dL*self.dS)) / (const.c.value*const.c.value))

	def reConfigure(self,configs):
		begin = time.clock()
		finalData = self.numbaSection(configs)
		print(time.clock()-begin)
		print("Printing maxes Now")
		print(np.max(finalData.imag))
		print(np.max(finalData.real))
		self.tree = WrappedTree()
		self.tree.setDataFromNumpy(finalData)
		self.preCalculating = False

	def numbaSection(self,configs):
		self.preCalculating = True
		# print(dL)
		# print(dLS)
		self.configs = configs
		incidentAngle = np.ndarray((self.configs.canvasDim.x,self.configs.canvasDim.y),dtype = np.complex)
		for i in range(0,self.configs.canvasDim.x):
			for j in range(0,self.configs.canvasDim.y):
				incidentAngle[i][j] = complex((i-self.configs.canvasDim.x/2),(j-self.configs.canvasDim.y/2))*configs.dTheta
		lensePlanePositions = incidentAngle*self.dL
		deflectionAngles = self.galaxy.alphaAt(lensePlanePositions)
		finalData = lensePlanePositions+((incidentAngle+deflectionAngles)*self.dLS)
		return finalData

	def start(self, canvas):
		# periodogram_opencl()
		self.reConfigure(self.configs)
		self.calculating = True
		width = self.configs.canvasDim.x
		height = self.configs.canvasDim.y
		if not self.preCalculating:
			self.byteArray = np.full(shape=(width,height),fill_value = 0.0)
			self.galaxy.draw(canvas,self.configs.dTheta)
			self.quasar.draw(canvas,self.configs.dTheta)
			while self.calculating:
				self.drawFrame(canvas)

	def getPixelCount(self,position):
		self.quasar.setPos(position)
		ret = len(self.tree.getInBall(self.quasar.observedPosition,self.quasar.radius))
		return ret


	def restart(self):
		self.calculating = False
		self.time = 0.0
	def pause(self):
		self.calculating = False
	def drawFrame(self,canvas):
		width = self.configs.canvasDim.x
		height = self.configs.canvasDim.y
		dt = self.configs.dt
		coloredPixels = np.full(shape=(width,height),fill_value = 0, dtype = np.int)
		self.quasar.setTime(self.time)
		ret = self.tree.getInBall(self.quasar.observedPosition,self.quasar.radius.value)
		for pixel in ret:
			coloredPixels[int(pixel.real),int(pixel.imag)] = 2
		canvas.plotArray(coloredPixels)
		self.time += dt
		
	def calcDeflections(self):
		pass
