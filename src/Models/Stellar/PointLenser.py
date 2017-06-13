import math

from Models import Movable
from Utility import Vector2D
from Utility import zeroVector
from Views.Drawer.ShapeDrawer import drawSolidCircle
import astropy.units as u


# from Views.Drawer.PyShapeDrawer import drawSolidCircle
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
		print("Calling this")
		center = (self.position)/parameters.dTheta.value
		center = Vector2D(int(center.x+parameters.canvasDim/2),int(center.y+parameters.canvasDim/2))
		radius = int(math.sqrt(self.mass.value + 2))
# 		radius = int(self.mass.value + 2)
		drawSolidCircle(int(center.x),int(center.y),radius,img)
# 		img[center.x,center.y] = self._Drawable__colorKey
# 		img[center.x+1,center.y] = self._Drawable__colorKey
# 		img[center.x+1,center.y+1] = self._Drawable__colorKey
# 		img[center.x,center.y+1] = self._Drawable__colorKey


	@property
	def mass(self):
		return self.__mass.to('solMass')
	
	
	def drawSolidCircle(self,x0,y0,r,canvas):
		rSquared = r * r
		canvasDim = canvas.shape[0]    
		for x in range(0,r+1):
			for y in range(0,r+1):
				if x*x + y*y <= rSquared:
					if x0+x > 0 and y0+y > 0 and x0+x < canvasDim and y0+y < canvasDim:
						canvas[x0+x,y0+y] = 3
					if x0+x > 0 and y0-y > 0 and x0+x < canvasDim and y0-y < canvasDim:
						canvas[x0+x,y0-y] = 3
					if x0-x > 0 and y0+y > 0 and x0-x < canvasDim and y0+y < canvasDim:
						canvas[x0-x,y0+y] = 3
					if x0-x > 0 and y0-y > 0 and x0-x < canvasDim and y0-y < canvasDim:
						canvas[x0-x,y0-y] = 3
