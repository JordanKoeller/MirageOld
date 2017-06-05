from Models import Movable
from Utility import Vector2D
from Utility import zeroVector
import astropy.units as u


class PointLenser(Movable):
	__mass = 0
	def __init__(self, position = None, mass = u.Quantity(0),velocity=zeroVector):
		Movable.__init__(self,position,velocity)
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
		center = (self.position)/parameters.dTheta.value
		center = Vector2D(int(center.x+parameters.canvasDim/2),int(center.y+parameters.canvasDim/2))
		img[center.x,center.y] = self._Drawable__colorKey
		img[center.x+1,center.y] = self._Drawable__colorKey
		img[center.x+1,center.y+1] = self._Drawable__colorKey
		img[center.x,center.y+1] = self._Drawable__colorKey


	@property
	def mass(self):
		return self.__mass.to('solMass')
