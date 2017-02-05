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


class PointLenser(Drawable):
	__mass = 0
	def __init__(self, position = None, mass = u.Quantity(0)):
		self.updateDrawable(position = position, colorKey = 2)
		self.__mass = mass 

	def draw(self,img,configs):
		center = (self.position - configs.frameShift)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim.x/2),int(center.y+configs.canvasDim.y/2))
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






class Galaxy(Drawable,Cosmic):
	__velocityDispersion = u.Quantity(0,'km/s')
	__pcntStar = 0
	__shear = None
	__stars = []

	def __init__(self, redshift = 0.0, velocityDispersion = u.Quantity(0,'km/s'), percenterStars = 0, shearMag = 0, shearAngle = 0, center = zeroVector, shear = None):
		self.updateDrawable(center, 2)
		self.updateCosmic(redshift)
		self.__velocityDispersion = velocityDispersion
		self.__pcntStar = percenterStars
		self.__shear = shear or ShearLenser(shearMag,shearAngle)

	def setPos(self, einsteinRadius, theta = math.pi):
		x = math.sin(theta)
		y = -math.cos(theta)
		self.updateDrawable(position = Vector2D(x*einsteinRadius, y*einsteinRadius, einsteinRadius.unit))

	def generateStars(self,einsteinRadius): #RTODO
		einsteinRadius = einsteinRadius
		self.__stars = []
		for i in range(0,20):
			self.__stars.append(PointLenser(Vector2D(rand.random()-0.5,
					rand.random()-0.5,'rad')*einsteinRadius*3,
				const.M_sun*5e11))

	def draw(self,img,configs):
		for star in self.__stars:
			star.draw(img,configs)
		center = self.position + (configs.canvasDim/2)
		for i in range(-1,2,1):
			for j in range(-1,2,1):
				img.setPixel(center.x+i,center.y+j,self.colorKey)


	def getStarArray(self): #TODO
		starCount = 20
		DTYPE_T = np.dtype([('lenserType',np.int32),
			('mass', np.float32),
			('x',np.float32),
			('y',np.float32),
			('radius',np.float32)])
		arr = np.ndarray(starCount+2,dtype = DTYPE_T)
		for i in range(0,starCount-2):
			star = self.__stars[i]
			arr[i] = (0,star.mass.value,star.position.to('rad').x,star.position.y,0.0)
		arr[starCount-2] = (1,self.velocityDispersion.value,self.position.to('rad').x,self.position.y,00)
		arr[starCount-1] = (2,self.shear.magnitude,self.position.x,self.position.y,self.shear.angle.to('rad').value)
		# print(arr)
		return arr

	def update(self,redshift = None, velocityDispersion = None, numStars = None, shearMag = None, shearAngle = None):
		self.updateCosmic(redshift)
		self.__velocityDispersion = velocityDispersion or self.__velocityDispersion
		self.__shear.update(shearMag,shearAngle)


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
	def numStars(self):
		return 20






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
		print("radius = "+ str(self.__radius))

	def update(self, redshift = None, position = None, radius = None, velocity = None):
		self.updateCosmic(redshift = redshift)
		self.updateDrawable(position = position)
		self.__velocity = velocity or self.__velocity
		self.__observedPosition = self.position
		self.__radius = radius or self.__radius
		print("radius = "+ str(self.__radius.to('rad')))
		print("position = "+ str(self.position.to('rad')))


	def draw(self, img, configs):
		begin = time.clock()
		center = (self.observedPosition - configs.frameShift)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim.x/2),int(center.y+configs.canvasDim.y/2))
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
		self.__observedPosition = (self.velocity * t)


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

