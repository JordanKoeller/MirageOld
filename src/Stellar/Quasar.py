import numpy as np
import astropy.units as u
from Utility import Vector2D
from Utility.Vector2D import zeroVector
from astropy import constants as const
import random as rand
from matplotlib.patches import Circle
import math
import time
from Stellar.Drawable import Drawable
from Stellar.Cosmic import Cosmic

class Quasar(Drawable,Cosmic):
	__radius = 0
	__observedPosition = zeroVector
	__velocity = zeroVector


	def __init__(self,redshift = 0,radius = u.Quantity(0,'rad'),position = zeroVector,velocity = zeroVector):
		self.__velocity = velocity
		self.__observedPosition = position
		self.__radius = radius
		self.updateDrawable(position = position,colorKey = 3)
		self.updateCosmic(redshift = redshift)

	def update(self, redshift = None, position = None, radius = None, velocity = None):
		self.updateCosmic(redshift = redshift)
		self.updateDrawable(position = position)
		if velocity != None:
			self.__velocity = velocity
		self.__observedPosition = self.position
		if radius != None:
			self.__radius = radius


	def draw(self, img, parameters):
		begin = time.clock()
		center = (self.observedPosition)/parameters.dTheta.value
		center = Vector2D(int(center.x+parameters.canvasDim/2),int(center.y+parameters.canvasDim/2))
		radius = int(self.radius.value/parameters.dTheta.value)
		rSquared = radius * radius
		for x in range(0,radius+1):
			for y in range(0,radius+1):
				if x*x + y*y <= rSquared:
					if center.x+x > 0 and center.y+y > 0 and center.x+x < parameters.canvasDim and center.y+y < parameters.canvasDim:
						img[center.x+x,center.y+y] = self._Drawable__colorKey
					if center.x+x > 0 and center.y-y > 0 and center.x+x < parameters.canvasDim and center.y-y < parameters.canvasDim:
						img[center.x+x,center.y-y] = self._Drawable__colorKey
					if center.x-x > 0 and center.y+y > 0 and center.x-x < parameters.canvasDim and center.y+y < parameters.canvasDim:
						img[center.x-x,center.y+y] = self._Drawable__colorKey
					if center.x-x > 0 and center.y-y > 0 and center.x-x < parameters.canvasDim and center.y-y < parameters.canvasDim:
						img[center.x-x,center.y-y] = self._Drawable__colorKey

	def pixelRadius(self,dTheta):
		return (self.__radius.to('rad')/dTheta).value
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


	def setPos(self,x,y):
		self.__observedPosition = Vector2D(x,y)


defaultQuasar = Quasar(redshift = 0.073,
	position = Vector2D(-0.0003,0,"rad"),
	radius = u.Quantity(5,"arcsecond"),
	velocity = Vector2D(0,0,"rad"))

microQuasar = Quasar(redshift = 0.073,
	position = Vector2D(0,0,"rad"),
	radius = u.Quantity(1.7037e-6,"rad"),
	velocity = Vector2D(1.59016e-8,0,"rad"))
