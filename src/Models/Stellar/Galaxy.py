import astropy.units as u
from Utility import Vector2D
from Utility import zeroVector
from Models.Stellar.ShearLenser import ShearLenser
from Models.Stellar.Drawable import Drawable
from Models.Stellar.Cosmic import Cosmic
from Views.Drawer.ShapeDrawer import drawPointLensers
from Models.ParametersError import ParametersError
from Models.Model import Model

class Galaxy(Drawable, Cosmic):
	__velocityDispersion = u.Quantity(0, 'km/s')
	__pcntStar = 0
	__shear = None
	__stars = []

	def __init__(self, redshift=0.0, velocityDispersion=u.Quantity(0, 'km/s'), shearMag=0, shearAngle=0, percentStars=0, center=zeroVector, starVelocityParams = None, skyCoords= None, velocity=None,stars = []):
		Drawable.__init__(self)
		Cosmic.__init__(self)
		self.__velocityDispersion = velocityDispersion
		self.__pcntStar = percentStars / 100
		self.__shear = ShearLenser(shearMag, shearAngle)
		self.updateDrawable(position=center, colorKey=4)
		self.updateCosmic(redshift=redshift)
		self.__starVelocityParams = starVelocityParams
		self.__avgStarMass = 0.5
		self.skyCoords = skyCoords
		self.velocity = velocity
		self.__stars = stars

	def drawStars(self, img, parameters):
		if len(self.__stars) != 0:
			drawPointLensers(self.__stars, img, parameters)

	def drawGalaxy(self, img, parameters):
		center = Vector2D(self.position.x / parameters.dTheta.value + (parameters.canvasDim / 2), self.position.y / parameters.dTheta.value + (parameters.canvasDim / 2))
		for i in range(-2, 3, 1):
			for j in range(-2, 3, 1):
				if center.x + i > 0 and center.y + j > 0 and center.x + i < parameters.canvasDim and center.y + j < parameters.canvasDim:
					img[int(center.x + i), int(center.y + j)] = self.colorKey


	@property
	def starArray(self):
		if len(self.__stars) > 0:
			massArr = self.__stars[:,2]
			xArr = self.__stars[:,0]
			yArr = self.__stars[:,1]
			return (massArr, xArr, yArr)	
		else:
			return ([],[],[])
			
	@property
	def starVelocityParams(self):
		return self.__starVelocityParams
		
	def clearStars(self):
		self.__stars = []
		self.__avgStarMass = 0.5
			
			
	def moveStars(self, dt):
		self.__stars[:,0] = self.__stars[:,0] + self.__stars[:,3]*dt
		self.__stars[:,1] = self.__stars[:,1] + self.__stars[:,4]*dt

			
	def update(self, redshift=None, velocityDispersion=None, shearMag=None, shearAngle=None, center=None, percentStars=None, stars=[]):
		try:
			self.__velocityDispersion = velocityDispersion or self.__velocityDispersion
			self.__shear.update(shearMag, shearAngle)
			if percentStars != None:
				self.__pcntStar = percentStars
			if stars != []:
				self.__stars = stars
				self.__avgStarMass = sum(stars[:,2])/len(stars)
			self.updateDrawable(position=center)
			self.updateCosmic(redshift=redshift)
		except ParametersError as e:
			raise e

	def __str__(self):
		return "GALAXY:\n" + self.drawableString() + "\n" + self.cosmicString() + "\n" + self.shear.shearString() + "\nvelocity Dispersion = " + str(self.velocityDispersion) + "\nnumStars = " + str(self.numStars) + "\n\n"


	def __eq__(self, other):
		if self.isSimilar(other) and self.__stars == other.stars:
			return True
		else:
			return False
	
	def isSimilar(self,other):
		if other == None:
			return False
		if self.redshift != other.redshift:
			return False
		if self.percentStars != other.percentStars:
			return False
		if self.shear != other.shear:
			return False
		if self.center.to('arcsec') != other.center.to('arcsec'):
			return False
		if self.velocityDispersion != other.velocityDispersion:
			return False
		return True

	@property
	def velocityDispersion(self):
		return self.__velocityDispersion.to('km/s')

	@property
	def percentStars(self):
		return self.__pcntStar

	@property
	def shear(self):
		return self.__shear
	@property
	def shearMag(self):
		return self.__shear.magnitude

	@property
	def shearAngle(self):
		return self.__shear.angle

	@property
	def numStars(self):
		return len(self.__stars)

	@property
	def center(self):
		return self.position

	@property
	def stars(self):
		return self.__stars
	
	@property
	def averageStarMass(self):
		return self.__avgStarMass

	@property
	def apparentVelocity(self):
		relVel = self.velocity - Model.earthVelocity	
		rCart = relVel.to_cartesian()
		l,b = (self.skyCoords.galactic.l, self.skyCoords.galactic.b.to('rad'))
		theta, phi = (math.pi/2 - b, l)
		capTheta = rCart.x*math.cos(theta)*math.cos(phi)+rCart.y*math.cos(theta)*math.sin(phi) - rCart.z*math.sin(theta)
		capPhi = rCart.y*math.cos(phi)-rCart.x*math.sin(phi)
		return Vector2D(capTheta,capPhi,'km/s')


defaultGalaxy = Galaxy(redshift=0.0073,
	velocityDispersion=u.Quantity(1500, "km/s"),
	shearMag=0.3206,
	shearAngle=u.Quantity(30, 'degree'))

microGalaxy = Galaxy(redshift=0.0073,
	velocityDispersion=u.Quantity(1500, "km/s"),
	shearMag=0.3206,
	shearAngle=u.Quantity(30, 'degree'))

