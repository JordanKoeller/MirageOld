from __future__ import division
from Vector2D import Vector2D
from Vector2D import zeroVector
from stellar import Galaxy
from stellar import Quasar
from stellar import defaultQuasar
from stellar import defaultGalaxy
from MassFunction import MassFunction
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
	def __init__(self, isMicrolensing = False, autoConfiguring = False, galaxy = defaultGalaxy, quasar = defaultQuasar, dTheta = 600/800, canvasDim = 800, showGalaxy = True, showQuasar = True, starMassTolerance = 0.05, starMassVariation = None):
		self.__galaxy = galaxy
		self.__quasar = quasar
		self.__dTheta = dTheta
		self.__canvasDim = canvasDim
		self.showGalaxy = showGalaxy
		self.showQuasar = showQuasar
		self.__starMassTolerance = starMassTolerance
		self.__starMassVariation = starMassVariation
		self.__dLS = self.__calcdLS()
		self.__einsteinRadius = self.__calcEinsteinRadius()
		self.setAutoConfigure(autoConfiguring)
		self.setMicrolensing(isMicrolensing)

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
		return self.__einsteinRadius

	@property
	def dLS(self):
		return self.__dLS

	def __calcEinsteinRadius(self):
		return 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.__dLS/self.quasar.angDiamDist /((const.c**2).to('km2/s2'))

	def __calcdLS(self):
		return cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')

	def setMicrolensing(self,isMicrolensing):
		if isMicrolensing:
			self.__galaxy.update(center = Vector2D(-self.einsteinRadius,0,'rad')) #Will refactor later, once how this works is figured out
		else:
			self.__galaxy.update(center = zeroVector)



	def setAutoConfigure(self,isAutoConfiguring):
		if isAutoConfiguring:
			self.__dTheta = self.einsteinRadius/self.__canvasDim
		else:
			pass

	def isSimilar(self,other):
		"""Things that warrant recalculation:
			dTheta
			canvasDim
			isMicrolensing
			starMassTolerance(if lower)
			starMassVariation
			starMassFunction

			gRedshift,
			gVD
			gShearMag
			gShearAngle
			gCenter
			g%Smooth
			qRedshift


			Checks to make sure the two instances have the above parameters as equal
			"""
		if self.dTheta != other.dTheta:
			return False
		if self.canvasDim != other.canvasDim:
			return False
		if self.starMassTolerance < other.starMassTolerance:
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
		if self.starMassTolerance != other.starMassTolerance:
			return False
		if self.showQuasar != other.showQuasar:
			return False
		if self.showGalaxy != other.showGalaxy:
			return False
		return True
		# if self.isAutoConfiguring != other.isAutoConfiguring:
		# 	return False





		