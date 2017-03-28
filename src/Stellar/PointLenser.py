from Utility import Vector2D
from Utility.Vector2D import zeroVector
import astropy.units as u
from astropy import constants as const
import math
import numpy as np
from Stellar.Drawable import Drawable

class PointLenser(Drawable):
	__mass = 0
	def __init__(self, position = None, mass = u.Quantity(0)):
		self.__mass = mass 
		self.updateDrawable(position = position, colorKey = 2)

	def __eq__(self,other):
		if other == None:
			return False
		if self.position != other.position:
			return False
		if self.mass != other.mass:
			return False
		if self.colorKey != other.colorKey:
			return False
		return True

	def __neq__(self,other):
		return not self.__eq__(other)

	def draw(self,img,parameters):
		center = (self.position)/parameters.dTheta
		center = Vector2D(int(center.x+parameters.canvasDim/2),int(center.y+parameters.canvasDim/2))
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
