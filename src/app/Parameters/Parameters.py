from __future__ import division

import math

from astropy import constants as const
from astropy import units as u 
from astropy.cosmology import WMAP7 as cosmo
from scipy.stats import norm

from .ExperimentParams import ExperimentParams
import numpy as np 
import random as rand 

from ..Calculator.InitialMassFunction import Evolved_IMF
from ..Utility import Vector2D
from ..Utility.ParametersError import ParametersError
from .Stellar import Galaxy, Quasar, GalaxyJSONDecoder, QuasarJSONDecoder
from ..Utility.QuantityJSONEncoder import QuantityJSONEncoder, QuantityJSONDecoder
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
			res['dTheta'] = quantEncoder.encode(o.dTheta)
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
		galaxy = gd.decode(js['galaxy'])
		quasar = qd.decode(js['quasar'])
		canvasDim = js['canvasDim']
		dTheta = qDecode.decode(js['dTheta'])*canvasDim
		parameters = Parameters(galaxy,quasar,dTheta,canvasDim)
		if js['extraParameters']:
			decoder = ExperimentParamsJSONDecoder()
			extras = decoder.decode(js['extraParameters'])
			parameters.extras = extras
		return parameters

class Parameters(object):
	"""
class Parameters:<br>
-----------------------------------<br>
	ATTRIBUTES:<br>
	----------------<br>
		galaxy - information about the lensing system<br>
		quasar - information about the source object<br>
		dTheta - stores the width per pixel, measured in angular units<br>
		shear - stores information describing the shear of the system<br>
		canvasDim - size of the canvas being calculated, in terms of number of pixels across the square canvas<br>
		einsteinRadius - Einstein radius of the system, in units of angle<br>
		gravitationalRadius - gravitational radius of the quasar, dependent on its mass. Measured in units of angle<br>
		specialUnits - astropy.units.Quantity definition for units of angle to einstein radius, or gravitational radius<br>
		avgMassEinsteinRadius - einstein radius of a 1/2 solar mass point mass, measured in units of angle<br>
		stars - numpy array of masses, positions, and velocities of stars modeled by the galaxy<br>
		relativeShearAngle - angle between the trajectory of the quasar and external shear<br>
		dLS - angular diameter distance between the galaxy and source objects, measured in linear distance units<br>
		smoothMassOnScreen - amount of mass enclosed within the canvas as described by the SIS distribution. Measured in solar masses<br>
		queryQuasarX - x coordinate of the quasar in units of radians, linearly shifted to accomodate for a shifted center of galaxy<br>
		queryQuasarY - y coordinate of the quasar in units of radians, linearly shifted to accomodate for a shifted center of galaxy<br>
		queryQuasarRadius - radius of the quasar, measured in radians.<br>
		extras - extra parameters to describe a specific scenario. Examples include rendering settings for visualization, or trial variance information for batch runs.<br>
<br>
	METHODS:<br>
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
		
	def __init__(self, galaxy = Galaxy(), quasar = Quasar(), dTheta = u.Quantity(4/20,'arcsec'), canvasDim = 2000, showGalaxy = True, showQuasar = True, starMassTolerance = 0.05, starMassVariation = None,numStars = 0):
		self.__galaxy = galaxy
		self.__quasar = quasar
		self.__dTheta = u.Quantity(dTheta/canvasDim,'rad')
		self.__canvasDim = canvasDim
		self.showGalaxy = showGalaxy
		self.showQuasar = showQuasar
		self.numStars = numStars
		self.__starMassTolerance = starMassTolerance
		self.__starMassVariation = starMassVariation
		self.dt = 2.6e7
		self.time = 0
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
		print("Regenerating stars now.")
		m_stars = self.__galaxy.percentStars*self.smoothMassOnScreen
		generator = Evolved_IMF()
		m_stars = m_stars.value
		if m_stars < 1.0:
			print("NOT ENOUGH MASS FOR STAR FIELD. GENERATION TERMINATED")
			return
		starMasses = generator.generate_cluster(float(m_stars))[0]
		if self.galaxy.starVelocityParams != None:
			velocityMag = norm.rvs(loc = self.galaxy.starVelocityParams[0],
							scale = self.galaxy.starVelocityParams[1],
							size = len(starMasses)) #Loc = mean, scale = sigma, size = number
			velocityDir = np.random.rand(len(velocityMag),3) - 0.5
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
				x = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				y = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				starArray[i] = [x,y, starMasses[i],velocities[i,0],velocities[i,1]]
			self.__galaxy.update(stars=starArray)
			return starArray
		else:
			starArray = np.ndarray((len(starMasses),3))
			for i in range(0,len(starMasses)):
				x = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
				y = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.to('rad').value
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
	def starMassFunction(self):
		return self.__starMassFunction
	@property
	def starMassVariation(self):
		return self.__starMassVariation

	@property
	def einsteinRadius(self):
		return 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))
	@property
	def einsteinRadiusUnit(self):
		return u.def_unit('einstein_rad',self.einsteinRadius.value*u.rad)
	@property
	def gravitationalRadius(self):
		linearRg = (self.quasar.mass.to('kg')*const.G/const.c/const.c).to('m')
		angleRg = linearRg/self.quasar.angDiamDist.to('m')
		rgUnit = u.def_unit('r_g',angleRg.value*u.rad)
		return rgUnit

	@property
	def specialUnits(self):
		return [self.avgMassEinsteinRadius,self.gravitationalRadius]

	@property
	def avgMassEinsteinRadius(self):
		avgMass = 0.20358470458734301 #Average mass, in solMass of a generated star cluster of 10 million stars
		thetaE = 4*const.G*u.Quantity(avgMass,'solMass').to('kg')*self.dLS.to('m')/self.quasar.angDiamDist.to('m')/self.galaxy.angDiamDist.to('m')/const.c/const.c
		thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
		return thetaEUnit

	@property
	def displayQuasar(self):
		return self.showQuasar

	@property
	def displayGalaxy(self):
		return self.showGalaxy

	@property
	def displayStars(self):
		return self.showGalaxy
	@property
	def stars(self):
		return self.galaxy._Galaxy__stars

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
		print("Mass = "+str(ret))
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


	def isSimilar(self,other):
		if self.dTheta != other.dTheta:
			return False
		if self.canvasDim != other.canvasDim:
			return False
		if self.starMassVariation != other.starMassVariation:
			return False
		if not self.galaxy.isSimilar(other.galaxy):
			return False
		if self.quasar.redshift != other.quasar.redshift:
			return False
		return True

	@property
	def jsonString(self):
		encoder = ParametersJSONEncoder()
		return encoder.encode(self)

	def __eq__(self,other):
		if not self.isSimilar(other):
			return False
		if self.quasar != other.quasar:
			return False
		if self.showQuasar != other.showQuasar:
			return False
		if self.showGalaxy != other.showGalaxy:
			return False
		return True


	def __str__(self):
		return ("\nPARAMETERS:\ndTheta = " + str(self.dTheta)) + ("\ncanvasDim = " + str(self.canvasDim)) + "\n" + str(self.quasar) + str (self.galaxy) + ("\ndLS = "+ str(self.dLS)) + ("\nEinstein Radius = " + str(self.einsteinRadius) + "\n\nEXTRAS:\n"+str(self.extras))
	
