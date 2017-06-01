import numpy as np
import astropy.units as u
from Utility import Vector2D
from Utility.Vector2D import zeroVector
from astropy import constants as const
import random as rand
import math
import time
from Models import Drawable
from Models import Cosmic

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
		center = (self.observedPosition + parameters.galaxy.position)/parameters.dTheta.value
		center = Vector2D(int(center.x+parameters.canvasDim/2),int(center.y+parameters.canvasDim/2))
		radius = int(self.radius.value/parameters.dTheta.value)
		rSquared = radius * radius
		count = 0
		for x in range(0,radius+1):
			for y in range(0,radius+1):
				if x*x + y*y <= rSquared:
					if center.x+x > 0 and center.y+y > 0 and center.x+x < parameters.canvasDim and center.y+y < parameters.canvasDim:
						img[center.x+x,center.y+y] = self._Drawable__colorKey
						count += 1
					if center.x+x > 0 and center.y-y > 0 and center.x+x < parameters.canvasDim and center.y-y < parameters.canvasDim:
						img[center.x+x,center.y-y] = self._Drawable__colorKey
						count += 1
					if center.x-x > 0 and center.y+y > 0 and center.x-x < parameters.canvasDim and center.y+y < parameters.canvasDim:
						img[center.x-x,center.y+y] = self._Drawable__colorKey
						count += 1
					if center.x-x > 0 and center.y-y > 0 and center.x-x < parameters.canvasDim and center.y-y < parameters.canvasDim:
						img[center.x-x,center.y-y] = self._Drawable__colorKey
						count += 1

	def circularPath(self):
		vel = self.velocity.magnitude()
		x,y = self.observedPosition.asTuple
		tangent = 0
		try:
			tangent = -x/y
		except ZeroDivisionError as e:
			tangent = -0
		self.__velocity = Vector2D(1,tangent).normalized()*self.velocity.magnitude()

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

	def incrementTime(self,dt):
		self.__observedPosition = self.__observedPosition + self.velocity * dt

	def __str__(self):
		return "QUASAR:\n" + self.cosmicString() + "\n" + self.drawableString() + "\nvelocity = " + str(self.velocity) + "\nradius = " + str(self.radius) + "\n\n"


	def setPos(self,x,y = None):
		if y == None:
			self.__observedPosition = x
		else:
			self.__observedPosition = Vector2D(x,y)

defaultQuasar = Quasar(redshift = 0.073,
	position = Vector2D(-0.0003,0,"rad"),
	radius = u.Quantity(5,"arcsecond"),
	velocity = Vector2D(0,0,"rad"))

microQuasar = Quasar(redshift = 0.073,
	position = Vector2D(0,0,"rad"),
	radius = u.Quantity(1.7037e-6,"rad"),
	velocity = Vector2D(1.59016e-8,0,"rad"))
