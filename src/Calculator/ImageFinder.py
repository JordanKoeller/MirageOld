from scipy.optimize import broyden1 as Solver
import numpy as np 
import math
from astropy import constants as const
from Utility import Vector2D

class __ImageFinder(object):
	"""docstring for ImageFinder"""
	def __init__(self):
		pass
		# super(__ImageFinder, self).__init__()
		


	def __rootFunction1(self,xy):
		xy = [xy[0],xy[1]]
		res = math.sqrt((xy[0])**2 + (xy[1])**2)
		x = ((self.c[0] + self.c[1]/res - self.c[2])*xy[0] - self.c[3]*xy[1] - self.c[0]*self.s.x)
		y = ((self.c[0] + self.c[1]/res + self.c[2])*xy[1] - self.c[3]*xy[0] - self.c[0]*self.s.y)
		return [x,y] #Incorrect implimentation

	def __getCoefficients(self,parameters):
		p = parameters
		D = p.quasar.angDiamDist/p.dLS
		aSis = 4*math.pi*p.galaxy.velocityDispersion.to("m/s").value**2/(const.c**2).value #Need to check units
		gCos = p.galaxy.shearMag*math.cos(2*p.galaxy.shearAngle.to("rad").value) #Need to check units
		gSin = p.galaxy.shearMag*math.sin(2*p.galaxy.shearAngle.to("rad").value) #Need to check units
		return [D,aSis,gCos,gSin,1/(p.dTheta.value)]

	def getRoot(self,xGuess,yGuess,parameters):
		self.c = self.__getCoefficients(parameters) #Parameters
		self.s = (parameters.quasar.position - parameters.galaxy.position) #Source vector
		go = Solver(self.__rootFunction1,[xGuess,yGuess])
		ret = Vector2D(go[0],go[1])
		return ret

ImageFinder = __ImageFinder()