from __future__ import division

import math
from math import sin, cos, tan, atan, atan2, sqrt, pi

from astropy import constants as const
from astropy import units as u 
from astropy.cosmology import WMAP5 as cosmo

import numpy as np 
import random as rand 

# from .ExperimentParams import ExperimentParams
# from ..utility import Vector2D
# from ..utility.ParametersError import ParametersError
# from .stellar import Galaxy, Quasar
# from ..utility.QuantityJSONEncoder import QuantityJSONEncoder, QuantityJSONDecoder
# from .ExperimentParams import ExperimentParamsJSONDecoder


# class ParametersJSONEncoder(object):
# 	"""docstring for ParametersJSONEncoder"""
# 	def __init__(self):
# 		super(ParametersJSONEncoder, self).__init__()
	
# 	def encode(self,o):
# 		if isinstance(o,Parameters):
# 			res = {}
# 			quantEncoder = QuantityJSONEncoder()
# 			res['galaxy'] = o.galaxy.jsonString
# 			res['quasar'] = o.quasar.jsonString
# 			res['canvasDim'] = o.canvasDim
# 			res['dTheta'] = quantEncoder.encode(o.dTheta*o.canvasDim)
# 			if o._rawMag != None:
# 				res['rawMagnification'] = o._rawMag
# 			if o.extras is None:
# 				res['extraParameters'] = None
# 			else:
# 				res['extraParameters'] = o.extras.jsonString
# 			return res
# 		else:
# 			raise TypeError("Argument o must be of type Parameters.")

# class ParametersJSONDecoder(object):
# 	"""docstring for ParametersJSONDecoder"""
# 	def __init__(self):
# 		super(ParametersJSONDecoder, self).__init__()
		
# 	def decode(self,js):
# 		gd = GalaxyJSONDecoder()
# 		qd = QuasarJSONDecoder()
# 		qDecode = QuantityJSONDecoder()
# 		qmass = qDecode.decode(js['quasar']['mass'])
# 		with u.add_enabled_units([Parameters.calculateAvgMassEinsteinRadius(js['galaxy']['redshift'],js['quasar']['redshift']),Parameters.calculateGravRad(qmass,js['quasar']['redshift'])]):
# 			galaxy = gd.decode(js['galaxy'])
# 			quasar = qd.decode(js['quasar'])
# 			canvasDim = int(js['canvasDim'])
# 			# print(canvasDim)
# 			dTheta = qDecode.decode(js['dTheta'])
# 			# print(str(dTheta)+str("DTHETA HERE"))
# 			parameters = Parameters(galaxy,quasar,dTheta,canvasDim)
# 			# if 'ellipticity' in js:
# 			# 	parameters.ellipticity = js['ellipticity']
# 			# 	parameters.ellipAng = js['ellipAng']
# 			if 'rawMagnification' in js:
# 				parameters.setRawMag(js['rawMagnification'])
# 			if js['extraParameters']:
# 				decoder = ExperimentParamsJSONDecoder()
# 				extras = decoder.decode(js['extraParameters'])
# 				parameters.extras = extras
# 			return parameters

# class Parameters(object):
		
# 	def __init__(self, galaxy = None, quasar = None, dTheta = u.Quantity(4/20,'arcsec'),
# 				canvasDim = 2000, numStars = 0):
# 		self.__galaxy = galaxy
# 		self.__quasar = quasar
# 		self.__dTheta = u.Quantity(dTheta/canvasDim,'rad')
# 		self.__canvasDim = canvasDim
# 		self.numStars = numStars
# 		# self.ellipticity = 0.6974
# 		# self.ellipAng = 1.129
# 		self.ellipticity = 1.0
# 		self.ellipAng = 0.0
# 		self._rawMag = None

# 	def update(self,galaxy=None,quasar=None,dTheta=None,canvasDim=None):
# 		if galaxy:
# 			if isinstance(galaxy,Galaxy):
# 				self.__galaxy = galaxy
# 			else:
# 				raise ParametersError("Galaxy must be an instance of type Galaxy")
# 		if quasar:
# 			if isinstance(quasar,Quasar):
# 				self.__quasar = quasar
# 			else:
# 				raise ParametersError("Galaxy must be an instance of type Galaxy")
# 		if canvasDim:
# 			if isinstance(canvasDim,float) or isinstance(canvasDim,int):
# 				self.__dTheta = self.__dTheta*self.__canvasDim/canvasDim
# 				self.__canvasDim = canvasDim
# 			else:
# 				raise ParametersError("CanvasDim must be a numeric type")
# 		if dTheta:
# 			try:
# 				self.__dTheta = dTheta.to('rad')/self.__canvasDim
# 			except:
# 				raise ParametersError("dTheta must be an instance of astropy.units.Quantity, of a unit of angle")

# 	# def regenerate_stars(self):
# 	# 	if self.__galaxy.percentStars != 0:
# 	# 		from mirage.calculator import getMassFunction
# 	# 		from mirage.preferences import GlobalPreferences
# 	# 		star_sidelength = self.dTheta.to('rad')*self.canvasDim*(GlobalPreferences['starfield_scalefactor']+1)
# 	# 		m_stars = self.__galaxy.percentStars*self.smoothMassOnScreen(star_sidelength)
# 	# 		generator = getMassFunction()
# 	# 		random_number_generator = generator.random_number_generator
# 	# 		m_stars = m_stars.value
# 	# 		if m_stars < 1.0:
# 	# 			print("NOT ENOUGH MASS FOR STAR FIELD. GENERATION TERMINATED")
# 	# 			return
# 	# 		starMasses = generator.generate_cluster(float(m_stars))[0]
# 	# 		if self.galaxy.starVelocityParams != None:
# 	# 			velocityMag = random_number_generator.normal(loc = self.galaxy.starVelocityParams[0],
# 	# 							scale = self.galaxy.starVelocityParams[1],
# 	# 							size = len(starMasses)) #Loc = mean, scale = sigma, size = number
# 	# 			velocityDir = random_number_generator.rand(len(velocityMag),3) - 0.5
# 	# 			velocityDirMag = np.sqrt(velocityDir[:,0]**2 + velocityDir[:,1]**2+velocityDir[:,2]**2)
# 	# 			for i in range(0,len(starMasses)):
# 	# 				velocityDir[i,0] = velocityDir[i,0]/velocityDirMag[i]
# 	# 				velocityDir[i,1] = velocityDir[i,1]/velocityDirMag[i]
# 	# 			velocities = np.ndarray((len(velocityDir),2))
# 	# 			for i in range(0,len(starMasses)):
# 	# 				velocities[i] = [velocityDir[i,0]*velocityMag[i], velocityDir[i,1]*velocityMag[i]]
# 	# 			velocities = velocities/self.galaxy.angDiamDist.to('km').value
# 	# 			starArray = np.ndarray((len(starMasses),5))
# 	# 			for i in range(0,len(starMasses)): #PROTOCOL of X, Y, Mass, Vx, Vy
# 	# 				x = (random_number_generator.rand() - 0.5)*star_sidelength.value
# 	# 				y = (random_number_generator.rand() - 0.5)*star_sidelength.value
# 	# 				starArray[i] = [x,y, starMasses[i],velocities[i,0],velocities[i,1]]
# 	# 			self.__galaxy.update(stars=starArray)
# 	# 			return starArray
# 	# 		else:
# 	# 			starArray = np.ndarray((len(starMasses),3))
# 	# 			for i in range(0,len(starMasses)):
# 	# 				x = (random_number_generator.rand() - 0.5)*star_sidelength.value
# 	# 				y = (random_number_generator.rand() - 0.5)*star_sidelength.value
# 	# 				starArray[i] = [x,y, starMasses[i]]
# 	# 			self.__galaxy.update(stars=starArray)
# 	# 	else:
# 	# 		print("Set with no stars")
# 	# 		self.starArray = np.array([])
# 	# 		self.__galaxy.update(percentStars = 0.0)

# 	# def clear_stars(self):
# 	# 	self.__galaxy.update(percentStars = 0)
# 	# 	self.regenerate_stars()
# 	# 	return self
		
# 	@property
# 	def galaxy(self):
# 		return self.__galaxy
# 	@property
# 	def quasar(self):
# 		return self.__quasar

# 	@property
# 	def dTheta(self):
# 		return self.__dTheta
# 	@property
# 	def canvasDim(self):
# 		return self.__canvasDim

# 	@property
# 	def einsteinRadius(self):
# 		ret = 4 * math.pi * self.__galaxy.velocityDispersion * self.__galaxy.velocityDispersion * self.dLS/self.dS /((const.c**2).to('km2/s2'))
# 		ret = ret.value
# 		return u.Quantity(ret,'rad')
# 	@property
# 	def einsteinRadiusUnit(self):
# 		return u.def_unit('einstein_rad',self.einsteinRadius.value*u.rad)
# 	@property
# 	def gravitationalRadius(self):
# 		return Parameters.calculateGravRad(self.quasar.mass,self.quasar.redshift)

# 	@property
# 	def specialUnits(self):
# 		from mirage.models import SpecialUnitsList
# 		return SpecialUnitsList(self.avgMassEinsteinRadius,self.gravitationalRadius)

# 	@staticmethod
# 	def calculateAvgMassEinsteinRadius(gz,qz):
# 		avgMass = 0.247
# 		# avgMass = 0.20358470458734301
# 		dL = cosmo.angular_diameter_distance(gz).to('m')
# 		dS = cosmo.angular_diameter_distance(qz).to('m')
# 		dLS = cosmo.angular_diameter_distance_z1z2(gz,qz).to('m')
# 		thetaE = 4*const.G*u.Quantity(avgMass,'solMass').to('kg')*dLS/dL/dS/const.c/const.c
# 		thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
# 		return thetaEUnit

# 	@property
# 	def avgMassEinsteinRadius(self):
# 		return Parameters.calculateAvgMassEinsteinRadius(self.galaxy.redshift,self.quasar.redshift)

# 	# @staticmethod
# 	# def calculateGravRad(mass,qz):
# 	# 	linRG = (mass.to('kg')*const.G/const.c/const.c).to('m')
# 	# 	angG = linRG/cosmo.angular_diameter_distance(qz).to('m')
# 	# 	rgUnit = u.def_unit('r_g',angG*u.rad)
# 	# 	return rgUnit


# 	# @property
# 	# def stars(self):
# 	# 	return self.galaxy._Galaxy__stars

# 	@property
# 	def raw_magnification(self):
# 		return self._rawMag


# 	@property
# 	def dLS(self):
# 		return cosmo.angular_diameter_distance_z1z2(self.__galaxy.redshift,self.__quasar.redshift).to('lyr')

# 	# def smoothMassOnScreen(self,sidelength): # WILL NEED TO COME BACK TO THIS
# 	# 	sidelength = sidelength.value*self.galaxy.angDiamDist.to("m")
# 	# 	r_in = self.__galaxy.position.to('rad').magnitude()*self.__galaxy.angDiamDist.to('m')
# 	# 	ret = ((self.__galaxy.velocityDispersion**2)*sidelength*sidelength/2/const.G/r_in).to('solMass')
# 	# 	# print(ret)
# 	# 	return ret
	
# 	@property
# 	def pixelScale_angle(self):
# 		return self.dTheta.to('arcsec')
	

# 	def convergence(self,position):
# 		"""Given a position, calculates the convergence of the lens at that position.
		
# 		Calculates the convergence of the macro-lens at the specified position. Useful for comparing to published values for convergence at an image,
# 		to check that the model is behaving properly.
		
# 		Arguments:
# 			position {`Vector2D:mirage.utility.Vector2D`} -- Position at which to calculate convergence. Must be in angular units.
# 		"""

# 		assert isinstance(position, Vector2D)
# 		from math import sin, cos
# 		q = self.ellipticity
# 		tq = self.ellipAng
# 		position = position - self.galaxy.position
# 		xx = position.to('arcsec').x
# 		yy = position.to('arcsec').y
# 		x = xx*sin(tq)+yy*cos(tq)
# 		y = yy*sin(tq)-xx*cos(tq)
# 		b = self.einsteinRadius.to('arcsec').value
# 		return b/(2.0*(x*x+y*y/q/q)**(0.5))

# 		# position = (position - self.galaxy.position).to('rad').magnitude()
# 		# er = self.einsteinRadius.to('rad').value
# 		# return (1/2)*er/position

# 	def shear(self,position):
# 		'''Given a position, calculates the shear of the lens at that position.

# 		Calculates the Shear of the macro-lens at the specified position. Useful for comparing to published values for the shear of an image.
# 		Note that this is not a shear as in the external shear applied to the system. It is the shear value, coming from the aniosotropic component
# 		of the Jacobian matrix, mapping from the source plane to lens plane. In other words, it describes how much a circular image would be stretched,
# 		provided the image is at the specified location.
		
# 		[description]
		
# 		Arguments:
# 			position {`Vector2D:mirage.utility.Vector2D`} -- Position at which to calculate shear. Must be in angular units.
# 		'''
# 		return self.shear_vector(position).magnitude()

# 	def shear_vector(self,position:Vector2D) -> Vector2D:
# 		v = (position - self.galaxy.position).to('rad')
# 		b = self.einsteinRadius.value
# 		gam = self.galaxy.shearMag
# 		p = self.galaxy.shearAngle.to('rad').value
# 		s1 = (1/2)*(b*(v.y*v.y-v.x*v.x)/((v.x*v.x+v.y*v.y)**(1.5)) + 2*gam*math.cos(2*p))
# 		s2 = -b*v.x*v.y/((v.x*v.x+v.y*v.y)**(1.5))+gam*math.sin(2*p)
# 		return Vector2D(s1,s2)


# 	def magnification(self,position):
# 		#Comes from the inverse of the determinant of the Jacobian matrix.
# 		#1/((1-convergence)**2 - shear**2)
# 		return 1/((1-self.convergence(position))**2 - self.shear(position)**2)
	
# 	def setRawMag(self,value):
# 		print("RawMag set to" + str(value))
# 		self._rawMag = value

# 	# def setStars(self,stars):
# 	# 	self.__galaxy.update(stars = stars)

# 	# def incrementTime(self,dt):
# 	# 	self.time += dt
# 	# 	self.__quasar.incrementTime(dt)
	
# 	# def setTime(self,time):
# 	# 	self.time = time
# 	# 	self.__quasar.setTime(time)
		
# 	# def pixelToAngle(self,pixel): 
# 	# 	x,y = pixel.asTuple
# 	# 	x = x-self.canvasDim/2
# 	# 	y = y-self.canvasDim/2
# 	# 	x = self.dTheta.to('rad')*x 
# 	# 	y = self.dTheta.to('rad')*y 
# 	# 	delta = Vector2D(x.value,y.value,'rad')
# 	# 	return delta + self.galaxy.center.to('rad')
	
# 	# def angleToPixel(self,angle):
# 	# 	delta = angle - self.galaxy.center.to('rad')
# 	# 	x,y = delta.asTuple 
# 	# 	x = x/self.dTheta.to('rad').value 
# 	# 	y = y/self.dTheta.to('rad').value 
# 	# 	return (int(x+self.canvasDim/2),int(self.canvasDim/2+y))

# 	# @property
# 	# def queryQuasarX(self):
# 	# 	return self.quasar.observedPosition.to('rad').x

# 	# @property
# 	# def queryQuasarY(self):
# 	# 	return self.quasar.observedPosition.to('rad').y
				
# 	# @property
# 	# def queryQuasarRadius(self):
# 	# 	return self.quasar.radius.to('rad').value
	
# 	# def getExtras(self,keyword):
# 	# 	if keyword in self.extras:
# 	# 		return self.extras[keyword]
# 	# 	else:
# 	# 		return None
		
# 	def isSimilar(self,other):
# 		if self.dTheta != other.dTheta:
# 			return False
# 		if self.canvasDim != other.canvasDim:
# 			return False
# 		if not self.galaxy.isSimilar(other.galaxy):
# 			return False
# 		if self.quasar.redshift != other.quasar.redshift:
# 			return False
# 		return True

# 	def approximate_raw_magnification(self,radius):
# 		radius = radius.to('rad')
# 		other_area = math.pi*radius*radius
# 		this_area = self.quasar.area
# 		area_ratios = other_area.value/this_area.value
# 		#Based on ration o_r/t_r = o_p/t_p
# 		#o_p = o_r*t_p/t_r
# 		return area_ratios*self.raw_magnification 



# 	@property
# 	def jsonString(self):
# 		encoder = ParametersJSONEncoder()
# 		return encoder.encode(self)

# 	def copy(self):
# 		from copy import deepcopy
# 		return deepcopy(self)

# 	def __eq__(self,other):
# 		if not self.isSimilar(other):
# 			return False
# 		if self.quasar != other.quasar:
# 			return False
# 		return True


# 	def __str__(self):
# 		return ("\nPARAMETERS:\ndTheta = " + str(self.dTheta)) + ("\ncanvasDim = " + str(self.canvasDim)) + "\n" + str(self.quasar) + str (self.galaxy) + ("\ndLS = "+ str(self.dLS)) + ("\nEinstein Radius = " + str(self.einsteinRadius) + "\n\nEXTRAS:\n"+str(self.extras))
	


from mirage.utility import PixelRegion, Vector2D, Region, JSONable
from .stellar import Galaxy, Quasar, defaultGalaxy, defaultQuasar


class Parameters(JSONable):

	def __init__(self,
		galaxy:Galaxy,
		quasar:Quasar,
		rayfield:PixelRegion,
		starfield_factor:float = 1.5) -> None:
		self._quasar = quasar
		self._galaxy = galaxy
		self._rayfield = rayfield
		dim = self._rayfield.dimensions*starfield_factor
		area = Region(self._rayfield.center,dim)
		self._starfield = area
		self._raw_magnification = 1


	@property
	def quasar(self):
		return self._quasar
	
	@property
	def galaxy(self):
		return self._galaxy
	
	@property
	def rayfield(self):
		return self._rayfield

	@property
	def dLS(self):
		return cosmo.angular_diameter_distance_z1z2(self.galaxy.redshift,self.quasar.redshift)

	@property
	def dL(self):
		return self.galaxy.angDiamDist

	@property
	def dS(self):
		return self.quasar.angDiamDist

	@property
	def einstein_radius(self):
		ret = 4 * math.pi * self.galaxy.velocity_dispersion * self.galaxy.velocity_dispersion * self.dLS/self.dL /((const.c**2).to('km2/s2'))
		ret = ret.value
		return u.Quantity(ret,'rad')

	@property
	def einstein_radius_unit(self):
		return u.def_unit('einstein_rad',self.einstein_radius.value*u.rad)

	@property
	def gravitational_radius(self):
		return self.quasar.gravitational_radius

	@property
	def special_units(self):
		from mirage.models import SpecialUnitsList
		return SpecialUnitsList(self.avg_mass_einstein_radius,self.gravitational_radius, self.einstein_radius_unit)

	@staticmethod
	def static_special_units(point_mass:u.Quantity, quasar_mass:u.Quantity, galaxy_z:float, quasar_z:float):
		from astropy.cosmology import WMAP5 as cosmo
		dL = cosmo.angular_diameter_distance(galaxy_z)
		dS = cosmo.angular_diameter_distance(quasar_z)
		dLS = cosmo.angular_diameter_distance_z1z2(galaxy_z, quasar_z)
		scale_factor = dLS/dL/dS
		G = const.G
		c = const.c
		r_g = quasar_mass.to('kg')*G/c/c
		theta_E = 4 * G * point_mass * scale_factor/ c /c
		theta_EUnit = u.def_unit('theta_E',math.sqrt(theta_E.value)*u.rad)
		r_gUnit = u.def_unit('r_g',r_g.value*u.rad)
		return [theta_EUnit, r_gUnit]


	@property
	def avg_mass_einstein_radius(self):
		avgMass = 0.247
		thetaE = 4*const.G*u.Quantity(avgMass,'solMass').to('kg')*self.dLS/self.dL/self.dS/const.c/const.c
		thetaEUnit = u.def_unit('theta_E',math.sqrt(thetaE.value)*u.rad)
		return thetaEUnit


	def convergence(self,position:Vector2D):
		"""Given a position, calculates the convergence of the lens at that position.
		
		Calculates the convergence of the macro-lens at the specified position. Useful for comparing to published values for convergence at an image,
		to check that the model is behaving properly.
		
		Arguments:
			position {`Vector2D:mirage.utility.Vector2D`} -- Position at which to calculate convergence. Must be in angular units.
		"""

		# ellip = self.galaxy.ellipticity
		# q = ellip.magnitude.value
		# tq = ellip.angle.to('rad').value
		# xx = position.to('arcsec').x
		# yy = position.to('arcsec').y
		# x = xx*sin(tq)+yy*cos(tq)
		# y = yy*sin(tq)-xx*cos(tq)
		# b = self.einstein_radius.to('arcsec').value
		# return b/(2.0*(x*x+y*y/q/q)**(0.5))
		return 0.7

		# position = (position - self.galaxy.position).to('rad').magnitude()
		# er = self.einsteinRadius.to('rad').value
		# return (1/2)*er/position

	def shear_vector(self,position:Vector2D) -> Vector2D:
		v = position.to('rad')
		b = self.einstein_radius.to('rad').value
		shear = self.galaxy.shear
		gam = shear.magnitude.value
		p = shear.direction.to('rad').value
		s1 = (1/2)*(b*(v.y*v.y-v.x*v.x)/((v.x*v.x+v.y*v.y)**(1.5)) + 2*gam*math.cos(2*p))
		s2 = -b*v.x*v.y/((v.x*v.x+v.y*v.y)**(1.5))+gam*math.sin(2*p)
		return Vector2D(s1,s2)


	def shear(self,position:Vector2D) -> float:
		'''Given a position, calculates the shear of the lens at that position.

		Calculates the Shear of the macro-lens at the specified position. Useful for comparing to published values for the shear of an image.
		Note that this is not a shear as in the external shear applied to the system. It is the shear value, coming from the aniosotropic component
		of the Jacobian matrix, mapping from the source plane to lens plane. In other words, it describes how much a circular image would be stretched,
		provided the image is at the specified location.
		
		[description]
		
		Arguments:
			position {`Vector2D:mirage.utility.Vector2D`} -- Position at which to calculate shear. Must be in angular units.
		'''
		return self.shear_vector(position).magnitude()

	def magnification(self,position:Vector2D) -> float:
		shear = self.shear(position)
		conv = self.convergence(position)
		return 1/((1-conv)**2 - shear**2)

	def regenerate_stars(self,recycle_seed = True) -> None:
		region = self._starfield
		density = self.surface_mass_density
		self.galaxy.generate_stars(region,density)

	@property 
	def surface_mass_density(self) -> u.Quantity:
		sigma_cr = const.c*const.c*self.dS/(4*const.G*pi*self.dL*self.dLS)
		density = sigma_cr*self.convergence(self._starfield.center)
		return u.Quantity(density.value,'solMass/rad2')

	@property
	def raw_magnification(self):
		return self._raw_magnification

	def calculate_raw_magnification(self):
		from mirage.calculator import get_raw_magnification
		r = self.quasar.radius.to('rad').value
		rm = get_raw_magnification(self,r)
		self._raw_magnification = rm
	



	@property 
	def json(self) -> dict:
		ret = {}
		ret['quasar'] = self.quasar.json
		ret['galaxy'] = self.galaxy.json
		ret['ray_field'] = self._rayfield.json
		if self.galaxy.star_generator and self.galaxy.star_generator.percent_stars > 0:
			ret['star_field_factor'] = (self._starfield.dimensions/self._rayfield.dimensions).x
		return ret

	@classmethod
	def from_json(cls,js):
		galaxy = Galaxy.from_json(js['galaxy'])
		quasar = Quasar.from_json(js['quasar'])
		rf = PixelRegion.from_json(js['ray_field'])
		if 'star_field_factor' in js:
			sf_factor = js['star_field_factor']
			return Parameters(galaxy,quasar,rf,sf_factor)
		else:
			return Parameters(galaxy,quasar,rf)

	def is_similar(self,other):
		return self.galaxy.isSimilar(other.galaxy) and self.quasar.isSimilar(other.quasar) and self._rayfield == other._rayfield




	def copy(self):
		from copy import deepcopy
		return deepcopy(self)


