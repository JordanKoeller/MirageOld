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





class Entity(object):
	"""Abstract Class controlling definition and reassignment of geometric information for a stellar object.
		arguments passed in should all be astropy unit objects"""

	__position = zeroVector
	def __init__(self,redshift,position):
		self.__redshift = redshift
		self.__position = position


	def update(self,redshift = None,position = None):
		"""
		Allows access to update Entity's attributes.

		Args:
			redshift - Numeric value
			position - Vector2D of entity's displacement from center of screen. Unit of a measurement of angle.
		""" 
		self.__redshift = redshift or self.__redshift
		self.__position = position or self.__position

	@property
	def redshift(self):
		return self.__redshift

	@property
	def angDiamDist(self):
		"""
		Returns angular diameter distance to the entity, in units of light years.
		"""
		return cosmo.angular_diameter_distance(self.__redshift).to('lyr').value

	@property
	def position(self):
		"""
		returns a Vector2D of displacement from the center of screen, in units of radians.
		"""
		return self.__position.to('rad')

	def distanceTo(self,other):
		"""Returns the distance between two Entity instances."""
		return self.__position.distanceTo(other.position)



	def draw(self, img, configs, colorKey = 2):
		"""Draws the entity to the canvas.
		Args:
			img - QImage to be drawn to.
			dTheta - Numeric of angle between two pixels on the canvas.
			colorKey - Int specifying index of image's colourspace to color the circle.
				default value = 2
		"""
		center = (self.position - configs.frameShift)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim.x/2),int(center.y+configs.canvasDim.y/2))
		img.setPixel(center.x,center.y,colorKey)
		img.setPixel(center.x+1,center.y,colorKey)
		img.setPixel(center.x+1,center.y+1,colorKey)
		img.setPixel(center.x,center.y+1,colorKey)














class Lenser(Entity):#_t):
	"""Abstract Class controlling objects that exhibit lensing properties."""
	def __init__(self, redshift, position,mass,enumCode = 0):
		Entity.__init__(self,redshift,position)	
		self.__mass = mass
		self.__enumCode = enumCode

	def update(self, redshift = None, position = None, mass = None):
		Entity.update(self,redshift,position)
		self.__mass = mass or self.__mass

	@property
	def mass(self):
		return self.__mass.to('solMass').value

	@property
	def enumCode(self):
		return self.__enumCode













class PointLenser(Lenser):
	"""Describes a pont mass lensing object.
		Enum key: 0"""
	def __init__(self,redshift,position,mass):
		Lenser.__init__(self,redshift,position,mass,0)











class DistLenser(Lenser):
	"""Enum code # 1"""
	def __init__(self,redshift,position,mass):
		Lenser.__init__(self,redshift,position,mass,1)

	def draw(self, img, configs, colorKey = 3):
		"Draws the entity to the canvas. Abstract method instantiated by subtypes."
		center = (self.position - configs.frameShift)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim.x/2),int(center.y+configs.canvasDim.y/2))
		for i in range(-2,3):
			for j in range(-2,3):
				img.setPixel(center.x+i,center.y+j,colorKey)







class Shear(object):
	def __init__(self, strength, angle):
		self.__angle = angle.to('rad')
		self.__strength = strength
		self.enumCode = 2

	def draw(self, canvas, configs):
		pass

	@property
	def angle(self):
		return self.__angle.to('rad').value

	@property
	def strength(self):
		return self.__strength










class Quasar(Entity): 
	def __init__(self,redshift,position,radius,velocity):
		Entity.__init__(self,redshift,position)
		self.__radius = radius
		self.__velocity = velocity
		self.observedPosition = position
		self.__radius_linear = u.Quantity(radius.value * self.angDiamDist,'lyr')
		self.circle = None

	def update(self, redshift = None, position = None, radius = None, velocity = None):
		Entity.update(self,redshift,position)
		self.__radius = radius or self.__radius
		self.__velocity = velocity or self.__velocity
		self.observedPosition = position or self.observedPosition



	def draw(self, img, configs, colorKey = 2):
		begin = time.clock()
		center = (self.observedPosition - configs.frameShift)/configs.dTheta
		center = Vector2D(int(center.x+configs.canvasDim.x/2),int(center.y+configs.canvasDim.y/2))
		radius = int(self.radius/configs.dTheta)
		rSquared = radius * radius
		for x in range(0,radius+1):
			for y in range(0,radius+1):
				if x*x + y*y <= rSquared:
					img.setPixel(center.x + x, center.y + y,colorKey)
					img.setPixel(center.x - x, center.y + y,colorKey)
					img.setPixel(center.x - x, center.y - y,colorKey)
					img.setPixel(center.x + x, center.y - y,colorKey)


	@property
	def radius(self):
		return self.__radius.to('rad').value


	@property
	def velocity(self):
		return self.__velocity.to('rad')

	def setTime(self, t):
		self.observedPosition = self.position + (self.velocity * t)

	def setPos(self,position):
		self.observedPosition = position










class Galaxy(Entity):
	def __init__(self,redshift,velocityDispersion,shearMag, shearAngle,radius,numStars = 0, shiftedCenter = False):
		Entity.__init__(self,redshift,Vector2D(0,0,"rad"))
		self.__velocityDispersion = velocityDispersion
		self.__numStars = numStars+2
		self.__stars = []
		self.__radius = radius
		self.__shiftedCenter = shiftedCenter
		self.shear = Shear(shearMag,shearAngle)


	def update(self,redshift = None,velocityDispersion = None,radius = None,numStars = None,shearMag = None, shearAngle = None):
		Entity.update(self,redshift,Vector2D(0,0,'rad'))
		self.__numStars = numStars or self.__numStars
		self.__velocityDispersion = velocityDispersion or self.__velocityDispersion
		self.__radius = radius or self.__radius
		shearMag = shearMag or self.shear._Shear__strength
		shearAngle = shearAngle or self.shear._Shear__angle
		self.shear = Shear(shearMag,shearAngle)

	@property
	def numStars(self):
		return self.__numStars

	@property
	def radius(self):
		return self.__radius.to('rad').value

	@property
	def stars(self):
		return self.__stars

	def setShift(self,value, einsteinRadius, theta = math.pi):
		#### TODO ######
		x = math.sin(theta) # Strange because converts to astronomical angle convention
		y = -math.cos(theta)
		self.distribution.update(position = Vector2D(x,y)*einsteinRadius)
		##### TODO : Refactor to have galaxy not inherit from entity #####

	@property
	def velocityDispersion(self):
		return self.__velocityDispersion.to('km/s').value

	def draw(self, canvas, configs):
		for star in self.stars:
			star.draw(canvas,configs)
		self.distribution.draw(canvas,configs)

	def generateStars(self,einsteinRadius,):
		print("calling generateStars")
		self.__stars = []
		self.distribution = DistLenser(self.redshift,
			Vector2D(0.0,0.0,'rad'),
			self.__velocityDispersion)
		for i in range(0,self.numStars-2):
			self.stars.append(PointLenser(self.redshift,
				Vector2D(rand.random()-0.5,rand.random()-0.5,'rad')*einsteinRadius,
				const.M_sun*5e10))

	def alphaAt(self, position):
		# print("Calling")
		ret = np.zeros(position.shape,dtype=np.complex)
		for star in self.stars:
			ret += star.unscaledAlphaAt(position)
			# print(position)
		return ret*((4*const.G/(const.c*const.c)).to('lyr/solMass').value)

	def getStarArray(self):
		DTYPE_T = np.dtype([('lenserType',np.int32),
			('mass', np.float32),
			('x',np.float32),
			('y',np.float32),
			('radius',np.float32)])
		arr = np.ndarray(self.numStars,dtype = DTYPE_T) #ADD 2 TO THE SIZE OF THE ARRAY TO GET MORE VARIED TYPES
		for i in range(0,self.numStars-2):
			star = self.stars[i]
			arr[i] = (star.enumCode,np.float32(star.mass),np.float32(star.position.x),np.float32(star.position.y),self.radius)
		arr[self.numStars-2] = (1,np.float32(self.velocityDispersion),np.float32(self.distribution.position.x),np.float32(self.distribution.position.y),self.radius) #Distribution
		arr[self.numStars-1] = (2,np.float32(self.shear.strength),np.float32(self.position.x),np.float32(self.position.y),self.shear.angle) #shear
		# print(arr)
		return arr


# Possible better way to do things: 
	# store in the engine all the information necessary to do calculations. 
	# Can still have lenser classes, but more of like structs now, without functions.
	# Would help because currently, far too much intercommunication, and breaking of encapsulation.
	# Though would make things harder, especially with stars having different masses and so on.




defaultGalaxy = Galaxy(0.0073,
	u.Quantity(1500,"km/s"),
	0.3206,
	u.Quantity(30,'degree'),
	u.Quantity(0.0006155,"rad"),
	0)

microGalaxy = Galaxy(0.0073,
	u.Quantity(1500,"km/s"),
	0.3206,
	u.Quantity(30,'degree'),
	u.Quantity(3.155e-5,"rad"),
	100)

defaultQuasar = Quasar(0.073,
	Vector2D(-0.0003,0,"rad"),
	u.Quantity(2.272e-5,"rad"),
	Vector2D(15e-5,0,"rad"))

microQuasar = Quasar(0.073,
	Vector2D(0,0,"rad"),
	u.Quantity(1.7037e-6,"rad"),
	Vector2D(1.59016e-8,0,"rad"))
