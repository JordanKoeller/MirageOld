import numpy as np
import astropy.units as u
from Utility import Vector2D
from Utility.Vector2D import zeroVector
from astropy import constants as const
import random as rand
import math
import time
from Stellar.ShearLenser import ShearLenser
from Stellar.PointLenser import PointLenser
from Stellar.Drawable import Drawable
from Stellar.Cosmic import Cosmic
class Galaxy(Drawable,Cosmic):
	__velocityDispersion = u.Quantity(0,'km/s')
	__pcntStar = 0
	__shear = None
	__stars = []

	def __init__(self, redshift = 0.0, velocityDispersion = u.Quantity(0,'km/s'), shearMag = 0, shearAngle = 0, percentStars = 0, center = zeroVector):
		self.__velocityDispersion = velocityDispersion
		self.__pcntStar = percentStars/100
		self.__shear = ShearLenser(shearMag,shearAngle)
		self.updateDrawable(position = center, colorKey = 4)
		self.updateCosmic(redshift = redshift)

	def drawStars(self,img,parameters):
		for star in self.__stars:
			star.draw(img,parameters)

	def drawGalaxy(self,img,parameters):
		center = Vector2D(self.position.x/parameters.dTheta.value + (parameters.canvasDim/2),self.position.y/parameters.dTheta.value + (parameters.canvasDim/2))
		# center = Vector2D(self.position.x/parameters.dTheta.value + (parameters.canvasDim/2),self.position.y/parameters.dTheta.value + (parameters.canvasDim/2))
		for i in range(-2,3,1):
			for j in range(-2,3,1):
				if center.x + i > 0 and center.y + j > 0 and center.x + i < parameters.canvasDim and center.y + j < parameters.canvasDim:
					img[int(center.x+i),int(center.y+j)] = self.colorKey


	@property
	def starArray(self):
		massArr = np.ndarray(len(self.__stars)+1,dtype = np.float64)
		xArr = np.ndarray(len(self.__stars)+1,dtype = np.float64)
		yArr = np.ndarray(len(self.__stars)+1,dtype = np.float64)
		for i in range(0,len(self.__stars)):
			star = self.__stars[i]
			massArr[i] = star.mass.value
			xArr[i] = star.position.to('rad').x
			yArr[i] = star.position.y
		massArr[len(self.__stars)] = 0.0
		xArr[len(self.__stars)] = 0.0
		yArr[len(self.__stars)] = 0.0
		return (massArr,xArr,yArr)

	def setStarMasses(self,masses,parameters):
		for i in range(0,len(masses)):
			self.__stars.append(PointLenser(Vector2D(rand.random()-0.5,
					rand.random()-0.5,'rad')*(parameters.canvasDim-2)*parameters.dTheta.value,
				u.Quantity(masses[i],'solMass')))


	def update(self,redshift = None, velocityDispersion = None, shearMag = None, shearAngle = None, center = None,percentStars = None,stars = None):
		self.__velocityDispersion = velocityDispersion or self.__velocityDispersion
		self.__shear.update(shearMag,shearAngle)
		if percentStars != None:
			self.__pcntStar = percentStars
		if stars != None:
			self.__stars = stars
		self.updateDrawable(position = center)
		self.updateCosmic(redshift = redshift)

	def __str__(self):
		return "GALAXY:\n" + self.drawableString() + "\n" + self.cosmicString() + "\n" + self.shear.shearString() + "\nvelocity Dispersion = " + str(self.velocityDispersion) + "\nnumStars = " + str(self.numStars) + "\n\n"


	def __eq__(self,other):
		if other == None:
			return False
		if self.percentStars != other.percentStars:
			return False
		if self.shear != other.shear:
			return False
		if self.center != other.center:
			return False
		if self.velocityDispersion != other.velocityDispersion:
			return False
		return True

	@property
	def velocityDispersion(self):
		return self.__velocityDispersion.to('km/s')

	@property
	def percentStars(self):
		return self.__pcntStar

	@property
	def shear(self):
		return self.__shear
	@property
	def shearMag(self):
		return self.__shear.magnitude

	@property
	def shearAngle(self):
		return self.__shear.angle

	@property
	def numStars(self):
		return len(self.__stars)

	@property
	def center(self):
		return zeroVector

	@property
	def position(self):
		return zeroVector
	@property
	def stars(self):
		return self.__stars


defaultGalaxy = Galaxy(redshift = 0.0073,
	velocityDispersion = u.Quantity(1500,"km/s"),
	shearMag = 0.3206,
	shearAngle = u.Quantity(30,'degree'))

microGalaxy = Galaxy(redshift = 0.0073,
	velocityDispersion = u.Quantity(1500,"km/s"),
	shearMag = 0.3206,
	shearAngle = u.Quantity(30,'degree'))

