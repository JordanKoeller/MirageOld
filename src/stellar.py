from astropy.cosmology import WMAP7 as cosmo
import numpy as np
import astropy.units as u
from Vector2D import Vector2D
from Vector2D import zeroVector
from astropy import constants as const
import random as rand
from numba import jit
from matplotlib.patches import Circle
import math
import time


class Drawable(object):
	__position = zeroVector
	__colorKey = 0

	def draw(self, img, configs):
		"""Draws the entity to the canvas.
		Args:
			img - QImage to be drawn to.
			configs - Configs class instance, specifying how to draw the entity.
		"""

	def updateDrawable(self, position = None, colorKey = None):
		if position is not None:
			self.__position = position
		if colorKey is not None:
			self.__colorKey = colorKey


	def setPos(self,position):
		self.__position = position

	@property
	def position(self):
		return self.__position

	@property
	def colorKey(self):
		return self.__colorKey

	def drawableString(self):
		return "postion = " + str(self.position)

class Cosmic(object):
	__redshift = 0.0

	@property
	def angDiamDist(self):
		return cosmo.angular_diameter_distance(self.__redshift).to('lyr')

	@property
	def redshift(self):
		return self.__redshift

	def updateCosmic(self,redshift = None):
		if redshift is not None:
			self.__redshift = redshift

	def cosmicString(self):
		return "redshift = " + str(self.redshift) + "\nAngDiamDist = " + str(self.angDiamDist)

class PointLenser(Drawable):
	__mass = 0
	def __init__(self, position = None, mass = u.Quantity(0)):
		self.updateDrawable(position = position, colorKey = 2)
		self.__mass = mass 

	def draw(self,img,configs):
		center = (self.position)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim/2),int(center.y+configs.canvasDim/2))
		img.setPixel(center.x,center.y,self._Drawable__colorKey)
		img.setPixel(center.x+1,center.y,self._Drawable__colorKey)
		img.setPixel(center.x+1,center.y+1,self._Drawable__colorKey)
		img.setPixel(center.x,center.y+1,self._Drawable__colorKey)


	def unscaledAlphaAt(self, position):
		"Returns a complex number, representing the unscaled deflection angle at the point pt."
		pos = self.position.toComplex()
		mass = self.mass.to('solMass')
		deltaR = pos-position
		r = np.absolute(deltaR)
		return deltaR * 0.12881055652653947 * (mass/(r*r))


	@property
	def mass(self):
		return self.__mass.to('solMass')


class ShearLenser(object):
	__mag = 0
	__angle = 0

	def __init__(self,mag,angle):
		self.__mag = mag
		self.__angle = angle

	def update(self,mag = None, angle = None):
		self.__mag = mag or self.__mag
		self.__angle = angle or self.__angle

	def unscaledAlphaAt(self, position):
		pass
	@property
	def magnitude(self):
		return self.__mag

	@property
	def angle(self):
		return self.__angle.to('rad')

	def shearString(self):
		return "shearMag = " + str(self.magnitude) + "\nshearAngle = " + str(self.angle)





class Galaxy(Drawable,Cosmic):
	__velocityDispersion = u.Quantity(0,'km/s')
	__pcntStar = 0
	__shear = None
	__stars = []
	__numStars = 0

	def __init__(self, redshift = 0.0, velocityDispersion = u.Quantity(0,'km/s'), percenterStars = 0, shearMag = 0, shearAngle = 0, center = zeroVector, numStars = 0):
		self.updateDrawable(center, 4)
		self.updateCosmic(redshift)
		self.__velocityDispersion = velocityDispersion
		self.__pcntStar = percenterStars
		self.__shear = ShearLenser(shearMag,shearAngle)
		self.__numStars = numStars

	def setPos(self, einsteinRadius, theta = math.pi):
		x = math.sin(theta)
		y = -math.cos(theta)
		self.updateDrawable(position = Vector2D(x*einsteinRadius, y*einsteinRadius, einsteinRadius.unit))

	def generateStars(self, configs): #RTODO
		self.__stars = []
		for i in range(0,self.__numStars):
			self.__stars.append(PointLenser(Vector2D(rand.random()-0.5,
					rand.random()-0.5,'rad')*(configs.canvasDim-2)*configs.dTheta,
				const.M_sun))

	def draw(self,img,configs, displayGalaxy):
		for star in self.__stars:
			star.draw(img,configs)
		if displayGalaxy:
			center = Vector2D(self.position.x/configs.dTheta + (configs.canvasDim/2),self.position.y/configs.dTheta + (configs.canvasDim/2))
			for i in range(-2,3,1):
				for j in range(-2,3,1):
					img.setPixel(center.x+i,center.y+j,self.colorKey)


	def getStarArray(self):
		massArr = np.ndarray(self.__numStars+1,dtype = np.float64)
		xArr = np.ndarray(self.__numStars+1,dtype = np.float64)
		yArr = np.ndarray(self.__numStars+1,dtype = np.float64)
		for i in range(0,self.__numStars):
			star = self.__stars[i]
			massArr[i] = star.mass.value
			xArr[i] = star.position.to('rad').x
			yArr[i] = star.position.y
		massArr[self.__numStars] = 0.0
		xArr[self.__numStars] = 0.0
		yArr[self.__numStars] = 0.0
		return (massArr,xArr,yArr)

	def update(self,redshift = None, velocityDispersion = None, shearMag = None, shearAngle = None, numStars = None, center = None):
		self.updateCosmic(redshift)
		self.__velocityDispersion = velocityDispersion or self.__velocityDispersion
		self.__shear.update(shearMag,shearAngle)
		# print(self.__numStars)
		self.__numStars = numStars or self.__numStars
		self.updateDrawable(center)
		# print(numStars)

	def unscaledAlphaAt(self, position):
		"Returns a complex number, representing the unscaled deflection angle at the point pt."
		for star in self.__stars:
			position += star.unscaledAlphaAt(position)
		position += self.shear.unscaledAlphaAt(position)
		pos = self.position.toComplex()
		mass = self.mass.to('solMass')
		deltaR = pos-position
		r = np.absolute(deltaR)
		position += deltaR * (self.velocityDispersion.value*self.velocityDispersion.value*28.83988945290979/(r))
		return position

	def __str__(self):
		return "GALAXY:\n" + self.drawableString() + "\n" + self.cosmicString() + "\n" + self.shear.shearString() + "\nvelocity Dispersion = " + str(self.velocityDispersion) + "\nnumStars = " + str(self.numStars) + "\n\n"

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
		return self.__numStars

	@property
	def center(self):
		return self.position
	@property
	def stars(self):
		return self.__stars






class Quasar(Drawable,Cosmic):
	__radius = 0
	__observedPosition = zeroVector
	__velocity = zeroVector


	def __init__(self,redshift = 0,radius = u.Quantity(0,'rad'),position = zeroVector,velocity = zeroVector):
		self.updateDrawable(position,3)
		self.updateCosmic(redshift)
		self.__velocity = velocity
		self.__observedPosition = position
		self.__radius = radius
		# print("radius = "+ str(self.__radius))

	def update(self, redshift = None, position = None, radius = None, velocity = None):
		self.updateCosmic(redshift = redshift)
		self.updateDrawable(position = position)
		self.__velocity = velocity or self.__velocity
		self.__observedPosition = self.position
		self.__radius = radius or self.__radius
		# print("radius = "+ str(self.__radius.to('rad')))
		# print("position = "+ str(self.position.to('rad')))


	def draw(self, img, configs):
		begin = time.clock()
		center = (self.observedPosition)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim/2),int(center.y+configs.canvasDim/2))
		radius = int(self.radius.value/configs.dTheta)
		rSquared = radius * radius
		for x in range(0,radius+1):
			for y in range(0,radius+1):
				if x*x + y*y <= rSquared:
					img.setPixel(center.x+x,center.y+y,self._Drawable__colorKey)
					img.setPixel(center.x+x,center.y-y,self._Drawable__colorKey)
					img.setPixel(center.x-x,center.y+y,self._Drawable__colorKey)
					img.setPixel(center.x-x,center.y-y,self._Drawable__colorKey)
	@property
	def velocity(self):
		return self.__velocity.to('rad')

	@property
	def radius(self):
		return self.__radius.to('rad')

	@property
	def position(self):
		return self.__observedPosition.to('rad')
	@property
	def observedPosition(self):
		return self.__observedPosition.to('rad')

	def setTime(self, t):
		self.__observedPosition = self._Drawable__position + (self.velocity * t)

	def __str__(self):
		return "QUASAR:\n" + self.cosmicString() + "\n" + self.drawableString() + "\nvelocity = " + str(self.velocity) + "\nradius = " + str(self.radius) + "\n\n"


	def setPos(self,position):
		self.__observedPosition = position



defaultGalaxy = Galaxy(redshift = 0.0073,
	velocityDispersion = u.Quantity(1500,"km/s"),
	shearMag = 0.3206,
	shearAngle = u.Quantity(30,'degree'))

microGalaxy = Galaxy(redshift = 0.0073,
	velocityDispersion = u.Quantity(1500,"km/s"),
	shearMag = 0.3206,
	shearAngle = u.Quantity(30,'degree'))

defaultQuasar = Quasar(redshift = 0.073,
	position = Vector2D(-0.0003,0,"rad"),
	radius = u.Quantity(2.272e-5,"rad"),
	velocity = Vector2D(15e-5,0,"rad"))

microQuasar = Quasar(redshift = 0.073,
	position = Vector2D(0,0,"rad"),
	radius = u.Quantity(1.7037e-6,"rad"),
	velocity = Vector2D(1.59016e-8,0,"rad"))

