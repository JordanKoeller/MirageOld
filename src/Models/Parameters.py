from __future__ import division
from Utility import Vector2D
from Calculator import Kroupa_2001
from astropy.cosmology import WMAP7 as cosmo
from astropy import constants as const
from astropy import units as u 
import math

class Parameters(object):
	"""Stores and processes all the information regarding the setup for a 
	gravitationally lensed system, along with how to display/calculate 
	the images.

	ALL POSSIBLE PARAMETERS:

	General:
		(control variable) is microlensing
		(control variable) auto configure
		dTheta [auto configure]
		canvasdim 
		showGalaxy [is microlensing, dtheta]
		showQuasar [is microlensing, dtheta]

	Galaxy:
		redshift
		velocityDispersion
		shear angle
		shear magnitude
		percent stars
		number of stars [dtheta, percent stars] ***
		star mass function
		star mass postprocessing info
		star mass function resolution
		center position [is microlensing]

	Quasar:
		redshift
		radius
		center position
		velocity
		base position"""
	def __init__(self, galaxy = None, quasar = None, dTheta = 600/800, canvasDim = 800, showGalaxy = True, showQuasar = True, starMassTolerance = 0.05, starMassVariation = None,numStars = 0, curveDim = Vector2D(800,200)):
		self.__galaxy = galaxy
		self.__quasar = quasar
		self.__dTheta = u.Quantity(dTheta/canvasDim,'rad')
		self.__canvasDim = canvasDim
		self.__curveDim = curveDim
		self.showGalaxy = showGalaxy
		self.showQuasar = showQuasar
		self.numStars = numStars
		self.__starMassTolerance = starMassTolerance
		self.__starMassVariation = starMassVariation
		self.dt = 0.1
		self.time = 0

	def generateStars(self):
		m_stars = self.__galaxy.percentStars*self.smoothMassOnScreen/100
		generator = Kroupa_2001()
		if m_stars < 1:
			print("Not enough mass in stars")
			m_stars = 10.0
		print("Starting generator with mass of "+str(m_stars))
		starMasses = generator.generate_cluster(m_stars)[0]
		print("Done.")
		self.__galaxy.setStarMasses(starMasses,self)

	@property
	def galaxy(self):
		return self.__galaxy
	@property
	def quasar(self):
		return self.__quasar
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
	def dLS(self):
		return cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')

	@property
	def smoothMassOnScreen(self): # WILL NEED TO COME BACK TO THIS
		l = (self.dTheta*self.canvasDim).to('rad').value*self.__galaxy.angDiamDist.to('m')
		r_in = self.__galaxy.position.to('rad').magnitude()*self.__galaxy.angDiamDist.to('m')
		ret = (l * self.__galaxy.velocityDispersion**2 * math.log(1+l/r_in)/2/const.G).to('solMass')
		print(ret)
		return ret.value

	@property
	def correctedVelocityDispersion(self):
		return math.sqrt(1-self.__galaxy.percentStars)*self.__galaxy.velocityDispersion

	def setStars(self,stars):
		self.__galaxy.update(stars = stars)

	def incrementTime(self,dt):
		self.time += dt
		self.__quasar.incrementTime(dt)
	
	def setTime(self,time):
		self.time = time
		self.__quasar.setTime(time)

	@property
	def queryQuasarX(self):
		return self.quasar.observedPosition.x

	@property
	def queryQuasarY(self):
		return self.quasar.observedPosition.y
				
	@property
	def queryQuasarRadius(self):
		return self.quasar.radius.value



	def isSimilar(self,other):
		if self.dTheta != other.dTheta:
			return False
		if self.canvasDim != other.canvasDim:
			return False
		if self.starMassVariation != other.starMassVariation:
			return False
		if self.galaxy != other.galaxy:
			return False
		if self.quasar.redshift != other.quasar.redshift:
			return False
		return True

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
		return ("dTheta = " + str(self.dTheta)) + ("\ncanvasDim = " + str(self.canvasDim)) + "\n" + str(self.quasar) + str (self.galaxy) + ("\ndLS = "+ str(self.dLS)) + ("\nEinstein Radius = " + str(self.einsteinRadius))