from __future__ import division

import math

from astropy import constants as const
from astropy import units as u 
from astropy.cosmology import WMAP7 as cosmo
from scipy.stats import norm
import numpy as np 
import random as rand 


from Calculator import Kroupa_2001
from Utility import Vector2D


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
		self.extras = None #Delegated member in charge of function-specific things, like display settings, light curve settings, etc.

	def generateStars(self):
		m_stars = self.__galaxy.percentStars*self.smoothMassOnScreen
		generator = Kroupa_2001()
		m_stars = m_stars.value
		if m_stars < 1.0:
			print("NOT ENOUGH MASS FOR STAR FIELD. GENERATION TERMINATED")
			return
		starMasses = generator.generate_cluster(m_stars)[0]
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
			velocities = velocities/self.galaxy.angDiamDist.to('km').value * 1e9
			print(velocities)
			starArray = np.ndarray((len(starMasses),5))
			for i in range(0,len(starMasses)): #PROTOCOL of X, Y, Mass, Vx, Vy
				x = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.value
				y = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.value
				starArray[i] = [x,y, starMasses[i],velocities[i,0],velocities[i,1]]
			return starArray
		else:
			starArray = np.ndarray((len(starMasses),3))
			for i in range(0,len(starMasses)):
				x = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.value
				y = (rand.random() - 0.5)* (self.canvasDim - 2)* self.dTheta.value
				starArray[i] = [x,y, starMasses[i]]
			return starArray
		
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
		ret = ((self.__galaxy.velocityDispersion**2)*l*l/2/const.G/r_in).to('solMass')
		return ret
	
	@property
	def pixelScale_angle(self):
		return self.dTheta.to('arcsec')
	
	@property
	def pixelScale_Rg(self): #Depends on mass, distance, pixel scale
		absRg = (self.__quasar.mass*const.G/const.c/const.c).to('m')
		angle = absRg/self.quasar.angDiamDist.to('m')
		pixAngle = self.pixelScale_angle.to('rad').value
		return pixAngle/angle
	
	@property
	def pixelScale_thetaE(self): #Depends on distances, pixel scale
		pixAngle = self.pixelScale_angle.to('rad').value
		thetaE = 4*const.G*u.Quantity(0.5,'solMass')*self.dLS/const.c/const.c/self.galaxy.angDiamDist/self.quasar.angDiamDist
		return pixAngle/math.sqrt(thetaE)
	
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
			print('failed dtheta')
			return False
		if self.canvasDim != other.canvasDim:
			print('failed canvasdim')
			return False
		if self.starMassVariation != other.starMassVariation:
			print('faield starmassvariation')
			return False
		if not self.galaxy.isSimilar(other.galaxy):
			print('failed galaxy')
			return False
		if self.quasar.redshift != other.quasar.redshift:
			print('faield qredshift')
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
		return ("\nPARAMETERS:\ndTheta = " + str(self.dTheta)) + ("\ncanvasDim = " + str(self.canvasDim)) + "\n" + str(self.quasar) + str (self.galaxy) + ("\ndLS = "+ str(self.dLS)) + ("\nEinstein Radius = " + str(self.einsteinRadius) + "\n\nEXTRAS:\n"+str(self.extras))
	
	