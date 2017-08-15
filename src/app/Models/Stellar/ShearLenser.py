from ...Utility.ParametersError import ParametersError

class ShearLenser(object):
	__mag = 0
	__angle = 0

	def __init__(self,mag,angle):
		self.__mag = mag
		self.__angle = angle

	def update(self,mag = None, angle = None):
		if mag != None:
			if isinstance(mag,float) or isinstance(mag,int):
				self.__mag = mag
			else:
				raise ParametersError("Shear Magnification must be a numeric type")
		if angle != None:
			try:
				self.__angle = angle.to('rad')
			except:
				raise ParametersError("Shear angle must be an instance of a astropy.units.Quantity, measuring angle.")

	def __eq__(self,other):
		if other == None:
			return False
		return self.magnitude == other.magnitude and self.angle == other.angle

	def __neq__(self,other):
		return not self.__eq__(other)

	def unscaledAlphaAt(self, position):
		pass
	@property
	def magnitude(self):
		return self.__mag

	@property
	def angle(self):
		return self.__angle.to('rad')

	def shearString(self):
		return "shearMag = " + str(self.magnitude) + "\nshearAngle = " + str(self.angle)
