
from Models import Cosmic
from Models import Movable
from Utility import Vector2D
from Utility.Vector2D import zeroVector
import astropy.units as u


class Quasar(Movable,Cosmic):
	__radius = 0



	def __init__(self,redshift = 0,radius = u.Quantity(0,'rad'),position = zeroVector,velocity = zeroVector):
		Movable.__init__(self,position,velocity)
		self.__radius = radius
		self.updateDrawable(position = position,colorKey = 3)
		self.updateCosmic(redshift = redshift)

	def update(self, redshift = None, position = None, radius = None, velocity = None):
		self.updateCosmic(redshift = redshift)
		self.updateDrawable(position = position)
		self.updateMovable(position,velocity)
		if radius != None:
			self.__radius = radius


	def draw(self, img, parameters):
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



	def pixelRadius(self,dTheta):
		return (self.__radius.to('rad')/dTheta).value

	@property
	def radius(self):
		return self.__radius.to('rad')


			
	def __str__(self):
		return "QUASAR:\n" + self.cosmicString() + "\n" + self.drawableString() + "\nvelocity = " + str(self.velocity) + "\nradius = " + str(self.radius) + "\n\n"



defaultQuasar = Quasar(redshift = 0.073,
	position = Vector2D(-0.0003,0,"rad"),
	radius = u.Quantity(5,"arcsecond"),
	velocity = Vector2D(0,0,"rad"))

microQuasar = Quasar(redshift = 0.073,
	position = Vector2D(0,0,"rad"),
	radius = u.Quantity(1.7037e-6,"rad"),
	velocity = Vector2D(1.59016e-8,0,"rad"))
