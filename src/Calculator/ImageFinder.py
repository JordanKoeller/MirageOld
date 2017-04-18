from scipy.optimize import broyden1 as Solver
import numpy as np 
import math


class __ImageFinder(object):
	"""docstring for ImageFinder"""
	def __init__(self):
		super(ImageFinder, self).__init__()
		


	def __rootFunction1(self,xy):
		x = (self.c[0] + self.c[1] - self.c[2])*xy[0] - self.c[3]*xy[1] - self.c[0]*self.s.x
		y = (self.c[0] + self.c[1] + self.c[2])*xy[1] - self.c[3]*xy[0] - self.c[0]*self.s.y
		return [x,y]

	def __getCoefficients(self,parameters):
		p = parameters
		D = p.quasar.angDiamDist/p.dLS
		aSis = 4*math.pi*p.galaxy.velocityDispersion**2/(const.c**2) #Need to check units
		gCos = p.galaxy.shearMag*math.cos(2*p.galaxy.shearAngle) #Need to check units
		gSin = p.galaxy.shearMag*math.sin(2*p.galaxy.shearAngle) #Need to check units
		return [D,aSis,gCos,gSin]

	def getRoot(self,xGuess,yGuess,parameters):
		self.c = self.__getCoefficients(parameters)
		self.s = (parameters.quasar.position - parameters.galaxy.position)
		return Vector2D(Solver(self.__rootFunction1,[xGuess,yGuess]))

ImageFinder = __ImageFinder()