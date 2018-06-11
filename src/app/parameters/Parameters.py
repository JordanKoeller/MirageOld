from __future__ import division

import math

from astropy import constants as const
from astropy import units as u 
from astropy.cosmology import WMAP7 as cosmo
from scipy.stats import norm

from .ExperimentParams import ExperimentParams
import numpy as np 
import random as rand 

from ..utility import Vector2D
from ..utility.ParametersError import ParametersError
from .stellar import Galaxy, Quasar, GalaxyJSONDecoder, QuasarJSONDecoder
from ..utility.QuantityJSONEncoder import QuantityJSONEncoder, QuantityJSONDecoder
from .ExperimentParams import ExperimentParamsJSONDecoder


class ParametersJSONEncoder(object):
	"""docstring for ParametersJSONEncoder"""
	def __init__(self):
		super(ParametersJSONEncoder, self).__init__()
	
	def encode(self,o):
		if isinstance(o,Parameters):
			res = {}
			quantEncoder = QuantityJSONEncoder()
			res['galaxy'] = o.galaxy.jsonString
			res['quasar'] = o.quasar.jsonString
			res['canvasDim'] = o.canvasDim
			res['dTheta'] = quantEncoder.encode(o.dTheta*o.canvasDim)
			if o._rawMag != None:
				res['rawMagnification'] = o._rawMag
			if o.extras is None:
				res['extraParameters'] = None
			else:
				res['extraParameters'] = o.extras.jsonString
			return res
		else:
			raise TypeError("Argument o must be of type Parameters.")

class ParametersJSONDecoder(object):
	"""docstring for ParametersJSONDecoder"""
	def __init__(self):
		super(ParametersJSONDecoder, self).__init__()
		
	def decode(self,js):
		gd = GalaxyJSONDecoder()
		qd = QuasarJSONDecoder()
		qDecode = QuantityJSONDecoder()
		qmass = qDecode.decode(js['quasar']['mass'])
		with u.add_enabled_units([Parameters.calculateAvgMassEinsteinRadius(js['galaxy']['redshift'],js['quasar']['redshift']),Parameters.calculateGravRad(qmass,js['quasar']['redshift'])]):
			galaxy = gd.decode(js['galaxy'])
			quasar = qd.decode(js['quasar'])
			canvasDim = int(js['canvasDim'])
			# print(canvasDim)
			dTheta = qDecode.decode(js['dTheta'])
			# print(str(dTheta)+str("DTHETA HERE"))
			parameters = Parameters(galaxy,quasar,dTheta,canvasDim)
			if 'rawMagnification' in js:
				parameters.setRawMag(js['rawMagnification'])
			if js['extraParameters']:
				decoder = ExperimentParamsJSONDecoder()
				extras = decoder.decode(js['extraParameters'])
				parameters.extras = extras
			return parameters

class Parameters(object):
	"""
	galaxy - information about the lensing system
	quasar - information about the source object
	dTheta - stores the width per pixel, measured in angular units
	shear - stores information describing the shear of the system
	canvasDim - size of the canvas being calculated, in terms of number of pixels across the square canvas
	einsteinRadius - Einstein radius of the system, in units of angle
	gravitationalRadius - gravitational radius of the quasar, dependent on its mass. Measured in units of angle
	specialUnits - astropy.units.Quantity definition for units of angle to einstein radius, or gravitational radius
	avgMassEinsteinRadius - einstein radius of a 1/2 solar mass point mass, measured in units of angle
	stars - numpy array of masses, positions, and velocities of stars modeled by the galaxy
	relativeShearAngle - angle between the trajectory of the quasar and external shear
	dLS - angular diameter distance between the galaxy and source objects, measured in linear distance units
	smoothMassOnScreen - amount of mass enclosed within the canvas as described by the SIS distribution. Measured in solar masses
	queryQuasarX - x coordinate of the quasar in units of radians, linearly shifted to accomodate for a shifted center of galaxy
	queryQuasarY - y coordinate of the quasar in units of radians, linearly shifted to accomodate for a shifted center of galaxy
	queryQuasarRadius - radius of the quasar, measured in radians.
	extras - extra parameters to describe a specific scenario. Examples include rendering settings for visualization, or trial variance information for batch runs.
	METHODS:
	----------------<br>
		isSimilar(parameters):Boolean<br>
			Compares this Parameters instance with a passed in Parameters instance, determines whether or not they are different enough<br>
			to warrant a re-ray-tracing the system<br>
<br>
		setStars(nummpy array):None<br>
			Replaces the star masses, positions, and velocities described by the galaxy with the data passed in.<br>
<br>
		regenerateStars():None<br>
			randomly generates a collection of stars, randomly sampling from the Kroupa_2001 distribution<br>
<br>
		update(galaxy,quasar,dTheta,canvasDim,extras,dt):None<br>
			replaces enclosed entities with those passed in. All arguments are key-word arguments.<br>
			In the event of an invalid argument, throws a ParametersError.<br>
			Note: if supplying the dTheta argument, the value passed in should be total angular width of the canvas. Not angular width per pixel.<br>
				All measurements with units must be passed in as an astropy.units.Quantity of appropriate units<br>
<br>
<br>
<br>
class Galaxy:<br>
-----------------------------------<br>
	ATTRIBUTES:<br>
	----------------<br>
		redshift - redshift to the galaxy from the observer (unitless)<br>
		velocityDispersion - velocity Dispersion of the modeled galaxy (km/s)<br>
		percentStars - fraction of mass present within the calculation canvas to be modeled as point masses, rather than in the SIS distribution<br>
		position - x,y coordinates of the center of the SIS distribution (angle)<br>
		center - alias for position<br>
		numStars - length of the stars array<br>
		stars - numpy array describing masses, positions, and velocities of all the stars modeled by the system (masses in solMass, positions in angular units, velocities in km/s)<br>
		shear - Shear object describing shear parameters for the system<br>
		starArray - returns three array-likes, the first is the masses of stars, then x and y coordinates of the stars (solMass,angle)<br>
<br>
	METHODS:<br>
	----------------<br>
		moveStars(dt):None<br>
			moves stars as described by their velocities over the time dt<br>
		<br>
		clearStars():None<br>
			deletes star data<br>
		<br>
		isSimilar(galaxy):Boolean<br>
			Compares this Galaxy instance with a passed in Galaxy instance, determines whether or not they are different enough<br>
			to warrant a re-ray-tracing the system<br>
<br>
		update(redshift, velocityDispersion, shearMag, shearAngle, center, percentStars, stars):None<br>
			replaces enclosed entities with those passed in. All arguments are key-word arguments.<br>
			In the even of an invalid argument, throws a ParametersError<br>
			All measurements with units must be passed in as an astropy.units.Quantity or Vec2D for 2-dimensional data with appropriate units.<br>
<br>
<br>
class Quasar:<br>
-----------------------------------<br>
	ATTRIBUTES:<br>
	----------------<br>
		redshift - redshift to the galaxy from the observer (unitless)<br>
		position - x,y coordinates of the center of the SIS distribution (angle)<br>
		center - alias for position<br>
		mass - mass of central black hole of the quasar, measured in solMass<br>
		radius - radius of the modeled quasar, measured in units of angle<br>
<br>
<br>
	METHODS:<br>
	----------------<br>
		isSimilar(galaxy):Boolean<br>
			Compares this Galaxy instance with a passed in Galaxy instance, determines whether or not they are different enough<br>
			to warrant a re-ray-tracing the system<br>
<br>
		update(redshift, velocityDispersion, shearMag, shearAngle, center, percentStars, stars):None<br>
			replaces enclosed entities with those passed in. All arguments are key-word arguments.<br>
			In the even of an invalid argument, throws a ParametersError<br>
			All measurements with units must be passed in as an astropy.units.Quantity or Vec2D for 2-dimensional data with appropriate units.<br>
<br>
		pixelRadius(dTheta):Numeric<br>
			given a measurement of angle per pixel, return the radius of the quasar in pixels.<br>

		super(ParametersJSONDecoder, self).__init__()
	"""
		
	def __init__(self, galaxy = Galaxy(), quasar = Quasar(), dTheta = u.Quantity(4/20,'arcsec'),
				canvasDim = 2000, numStars = 0):
		self.__galaxy = galaxy
		self.__quasar = quasar
		self.__dTheta = u.Quantity(dTheta/canvasDim,'rad')
		self.__canvasDim = canvasDim
		self.numStars = numStars
		self.dt = 2.6e7
		self.time = 0
		self._rawMag = None
		self.extras = None #Delegated member in charge of function-specific things, like display settings, light curve settings, etc.

	def update(self,galaxy=None,quasar=None,dTheta=None,canvasDim=None,extras=None,dt=None):
		if galaxy:
			if isinstance(galaxy,Galaxy):
				self.__galaxy = galaxy
			else:
				raise ParametersError("Galaxy must be an instance of type Galaxy")
		if quasar:
			if isinstance(quasar,Quasar):
				self.__quasar = quasar
			else:
				raise ParametersError("Galaxy must be an instance of type Galaxy")
		if canvasDim:
			if isinstance(canvasDim,float) or isinstance(canvasDim,int):
				self.__dTheta = self.__dTheta*self.__canvasDim/canvasDim
				self.__canvasDim = canvasDim
			else:
				raise ParametersError("CanvasDim must be a numeric type")
		if dTheta:
			try:
				self.__dTheta = dTheta.to('rad')/self.__canvasDim
			except:
				raise ParametersError("dTheta must be an instance of astropy.units.Quantity, of a unit of angle")
		if extras:
			self.extras = extras
		if dt:
			self.dt = dt

	def regenerateStars(self):
		m_stars = self.__galaxy.percentStars*self.smoothMassOnScreen
		from app.calculator import getMassFunction
		generator = getMassFunction()
		random_number_generator = generator.random_number_generator
		m_stars = m_stars.value
		if m_stars < 1.0:
			print("NOT ENOUGH MASS FOR STAR FIELD. GENERATION TERMINATED")
			return
		starMasses = generator.generate_cluster(float(m_stars))[0]
		if self.galaxy.starVelocityParams != None:
			velocityMag = norm.rvs(loc = self.galaxy.starVelocityParams[0],
							scale = self.galaxy.starVelocityParams[1],
							size = len(starMasses)) #Loc = mean, scale = sigma, size = number
			velocityDir = random_number_generator.rand(len(velocityMag),3) - 0.5
			velocityDirMag = np.sqrt(velocityDir[:,0]**2 + velocityDir[:,1]**2+velocityDir[:,2]**2)
			for i in range(0,len(starMasses)):
				velocityDir[i,0] = velocityDir[i,0]/velocityDirMag[i]
				velocityDir[i,1] = velocityDir[i,1]/velocityDirMag[i]
			velocities = np.ndarray((len(velocityDir),2))
			for i in range(0,len(starMasses)):
				velocities[i] = [velocityDir[i,0]*velocityMag[i], velocityDir[i,1]*velocityMag[i]]
			velocities = velocities/self.galaxy.angDiamDist.to('km').value
			starArray = np.ndarray((len(starMasses),5))
			for i in range(0,len(starMasses)): #PROTOCOL of X, Y, Mass, Vx, Vy
				x = (random_number_generator.rand() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				y = (random_number_generator.rand() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				starArray[i] = [x,y, starMasses[i],velocities[i,0],velocities[i,1]]
			self.__galaxy.update(stars=starArray)
			return starArray
		else:
			starArray = np.ndarray((len(starMasses),3))
			for i in range(0,len(starMasses)):
				x = (random_number_generator.rand() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				y = (random_number_generator.rand() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				starArray[i] = [x,y, starMasses[i]]
			self.__galaxy.update(stars=starArray)

		
	@property
	def galaxy(self):
		return self.__galaxy
	@property
	def quasar(self):
		return self.__quasar
	@property
	def shear(self):
		return self.__galaxy.shear
	@property
	def dTheta(self):
		return self.__dTheta
	@property
	def canvasDim(self):
		return self.__canvasDim
	@property
	def isMicrolensing(self):
		return self.__isMicrolensing

	@property
	def einsteinRadius(self):
		return 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))
	@property
	def einsteinRadiusUnit(self):
		return u.def_unit('einstein_rad',self.einsteinRadius.value*u.rad)
	@property
	def gravitationalRadius(self):
		return Parameters.calculateGravRad(self.quasar.mass,self.quasar.redshift)

	@property
	def specialUnits(self):
		from app.models import SpecialUnitsList
		return SpecialUnitsList(self.avgMassEinsteinRadius,self.gravitationalRadius)

	@staticmethod
	def calculateAvgMassEinsteinRadius(gz,qz):
		avgMass = 0.247
		# avgMass = 0.20358470458734301
		dL = cosmo.angular_diameter_distance(gz).to('m')
		dS = cosmo.angular_diameter_distance(qz).to('m')
		dLS = cosmo.angular_diameter_distance_z1z2(gz,qz).to('m')
		thetaE = 4*const.G*u.Quantity(avgMass,'solMass').to('kg')*dLS/dL/dS/const.c/const.c
		thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
		return thetaEUnit

	@staticmethod
	def calculateGravRad(mass,qz):
		linRG = (mass.to('kg')*const.G/const.c/const.c).to('m')
		angG = linRG/cosmo.angular_diameter_distance(qz).to('m')
		rgUnit = u.def_unit('r_g',angG*u.rad)
		return rgUnit

	@property
	def avgMassEinsteinRadius(self):
		return Parameters.calculateAvgMassEinsteinRadius(self.galaxy.redshift,self.quasar.redshift)

	@property
	def stars(self):
		return self.galaxy._Galaxy__stars

	@property
	def raw_magnification(self):
		return self._rawMag

	@property
	def relativeShearAngle(self):
		trajectory = None
		if self.extras:
			if isinstance(self.extras,ExperimentParams):
				trajectory = self.extras.pathEnd - self.extras.pathStart
				trajectory = trajectory.angle
			else:
				trajectory = self.quasar.velocity.angle
			astroTrajectory = math.pi/2 - trajectory
			if astroTrajectory < 0:
				astroTrajectory = math.pi*2 - astroTrajectory
			diff = self.shear.angle.to('rad') - u.Quantity(astroTrajectory,'rad')
			return diff.to('degree')

	@property
	def dLS(self):
		return cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')

	@property
	def smoothMassOnScreen(self): # WILL NEED TO COME BACK TO THIS
		l = (self.dTheta*self.canvasDim).to('rad').value*self.__galaxy.angDiamDist.to('m')
		r_in = self.__galaxy.position.to('rad').magnitude()*self.__galaxy.angDiamDist.to('m')
		ret = ((self.__galaxy.velocityDispersion**2)*l*l/2/const.G/r_in).to('solMass')
		return ret
	
	@property
	def pixelScale_angle(self):
		return self.dTheta.to('arcsec')
	
	@property
	def pixelScale_Rg(self): #Depends on mass, distance, pixel scale
		pixAngle = self.pixelScale_angle.to('rad').to(self.gravitationalRadius).value
		return pixAngle
	
	@property
	def pixelScale_thetaE(self): #Depends on distances, pixel scale
		pixAngle = self.pixelScale_angle.to('rad')
		return pixAngle.to(self.avgMassEinsteinRadius).value
	
	@property
	def quasarRadius_rg(self): #Depends on distances
		absRg = (self.__quasar.mass*const.G/const.c/const.c).to('m')
		angle = absRg/self.quasar.angDiamDist.to('m')
		return self.quasar.radius.to('rad').value/angle.value

	def convergence(self,position):
		"""Given a position, calculates the convergence of the lens at that position.
		
		Calculates the convergence of the macro-lens at the specified position. Useful for comparing to published values for convergence at an image,
		to check that the model is behaving properly.
		
		Arguments:
			position {`Vector2D:app.utility.Vector2D`} -- Position at which to calculate convergence. Must be in angular units.
		"""

		assert isinstance(position, Vector2D)
		position = (position - self.galaxy.position).to('rad').magnitude()
		er = self.einsteinRadius.value
		return (1/2)*er/position

	def shear(self,position):
		'''Given a position, calculates the shear of the lens at that position.

		Calculates the Shear of the macro-lens at the specified position. Useful for comparing to published values for the shear of an image.
		Note that this is not a shear as in the external shear applied to the system. It is the shear value, coming from the aniosotropic component
		of the Jacobian matrix, mapping from the source plane to lens plane. In other words, it describes how much a circular image would be stretched,
		provided the image is at the specified location.
		
		[description]
		
		Arguments:
			position {`Vector2D:app.utility.Vector2D`} -- Position at which to calculate shear. Must be in angular units.
		'''

		assert isinstance(position,Vector2D)
		v = (position - self.galaxy.position).to('rad')
		b = self.einsteinRadius.value
		gam = self.galaxy.shearMag
		p = self.galaxy.shearAngle.to('rad').value
		s1 = (1/2)*(b*(v.y*v.y-v.x*v.x)/((v.x*v.x+v.y*v.y)**(1.5)) + 2*gam*math.cos(2*p))
		s2 = -b*v.x*v.y/((v.x*v.x+v.y*v.y)**(1.5))+gam*math.sin(2*p)
		return math.sqrt(s1*s1+s2*s2)

	def magnification(self,position):
		#Comes from the inverse of the determinant of the Jacobian matrix.
		#1/((1-convergence)**2 - shear**2)
		return 1/((1-self.convergence(position))**2 - self.shear(position)**2)
	
	def setRawMag(self,value):
		print("RawMag set to" + str(value))
		self._rawMag = value

	def setStars(self,stars):
		self.__galaxy.update(stars = stars)

	def incrementTime(self,dt):
		self.time += dt
		self.__quasar.incrementTime(dt)
	
	def setTime(self,time):
		self.time = time
		self.__quasar.setTime(time)
		
	def pixelToAngle(self,pixel): 
		x,y = pixel.asTuple
		x = x-self.canvasDim/2
		y = y-self.canvasDim/2
		x = self.dTheta.to('rad')*x 
		y = self.dTheta.to('rad')*y 
		delta = Vector2D(x.value,y.value,'rad')
		return delta + self.galaxy.center.to('rad')
	
	def angleToPixel(self,angle):
		delta = angle - self.galaxy.center.to('rad')
		x,y = delta.asTuple 
		x = x/self.dTheta.to('rad').value 
		y = y/self.dTheta.to('rad').value 
		return (int(x+self.canvasDim/2),int(self.canvasDim/2+y))

	@property
	def queryQuasarX(self):
		return self.quasar.observedPosition.to('rad').x

	@property
	def queryQuasarY(self):
		return self.quasar.observedPosition.to('rad').y
				
	@property
	def queryQuasarRadius(self):
		return self.quasar.radius.to('rad').value
	
	def getExtras(self,keyword):
		if keyword in self.extras:
			return self.extras[keyword]
		else:
			return None
		
	def isSimilar(self,other):
		if self.dTheta != other.dTheta:
			return False
		if self.canvasDim != other.canvasDim:
			return False
		if not self.galaxy.isSimilar(other.galaxy):
			return False
		if self.quasar.redshift != other.quasar.redshift:
			return False
		return True

	def approximate_raw_magnification(self,radius):
		radius = radius.to('rad')
		other_area = math.pi*radius*radius
		this_area = self.quasar.area
		area_ratios = other_area.value/this_area.value
		#Based on ration o_r/t_r = o_p/t_p
		#o_p = o_r*t_p/t_r
		return area_ratios*self.raw_magnification 



	@property
	def jsonString(self):
		encoder = ParametersJSONEncoder()
		return encoder.encode(self)

	def __eq__(self,other):
		if not self.isSimilar(other):
			return False
		if self.quasar != other.quasar:
			return False
		return True


	def __str__(self):
		return ("\nPARAMETERS:\ndTheta = " + str(self.dTheta)) + ("\ncanvasDim = " + str(self.canvasDim)) + "\n" + str(self.quasar) + str (self.galaxy) + ("\ndLS = "+ str(self.dLS)) + ("\nEinstein Radius = " + str(self.einsteinRadius) + "\n\nEXTRAS:\n"+str(self.extras))
	

