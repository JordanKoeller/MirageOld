from astropy import units as u
import math
from math import log10, floor
class Vector2D(object): #TODO: Make compatable with astropy units package
	"""Simple 2-dimensional ordered pair with an x and y coordinate. Not recommended for heavy calculations."""
	def __init__(self,x,y,unit = None):
		"Simple 2-dimensional ordered pair with an x and y coordinate. Not recommended for heavy calculations."
		self.x = x
		self.y = y
		self.unit = unit
	def distanceTo(self, other,unit = None):
		"Calculates linear distance between two points"
		if unit != None:
			self.to(unit)
			other.to(unit)
		ex = self.x-other.x
		ey = self.y - other.y
		return math.sqrt(ex*ex+ey*ey)
	def magnitude(self,unit = None):
		"Calculates the magnitude of the point as if it were a vector."
		if unit != None:
			self.to(unit)
		return math.sqrt(self.x*self.x+self.y*self.y)
	def normalized(self,unit = None):
		"Returns a new unit vector in the direction of self."
		mag = self.magnitude(unit)
		return Vector2D(self.x/mag,self.y/mag)
	def toComplex(self):
		"Returns the Vector2D represented as a complex number"
		return complex(self.x,self.y)
	def to(self,unit):
		if self.unit == None:
			pass
		else:
			self.x = u.Quantity(self.x,self.unit)
			self.y = u.Quantity(self.y,self.unit)
			self.unit = unit
			self.x = self.x.to(self.unit).value
			self.y = self.y.to(self.unit).value
		return self

	def setUnit(self,unit):
		self.unit = unit
		return self

	def unitless(self):
		return Vector2D(self.x,self.y)

	@property
	def orthogonal(self):
		return Vector2D(self.y,self.x,self.unit)

	@property
	def asTuple(self):
		return (self.x,self.y)

	@property
	def angle(self):
		return math.atan2(self.y,self.x)
	def __add__(self, that):
		"Returns a new vector that is the sum of self and the passed in vector."
		return Vector2D(self.x+that.x,self.y+that.y)

	def __sub__(self, that):
		"Returns a new vector after subtracting the argument from self."
		return Vector2D(self.x-that.x,self.y-that.y)

	def __mul__(self, that):
		"Returns the dot product of two vectors."
		return Vector2D(self.x*that.x,self.y*that.y)

	def __mul__(self, scalar):
		"Returns a new vector after multiplying self by a scalar."
		return Vector2D(self.x*scalar,self.y*scalar)

	def __neg__(self):
		"Returns a new vector in the opposite direction of self."
		return Vector2D(-self.x,-self.y)
	def neg(self):
		return Vector2D(-self.x,-self.y)

	def __iadd__(self, that):
		"Adds a vector to self."
		self.x = self.x+that.x
		self.y = self.y+that.y
		return self
	
	def __isub__(self, that):
		"Subtracts a vector from self"
		self.x = self.x-that.x
		self.y = self.y-that.y
		return self

	def __imul__(self,scalar):
		"Multiplies self by a scalar."
		self.x = self.x*scalar
		self.y = self.y*scalar
		return self

	def __truediv__(self, scalar):
		"Divides self by a scalar."
		return self*(1/scalar)

	def __eq__(self,other):
		if other == None:
			return False
		return self.x == other.x and self.y == other.y and self.unit == other.unit

	def __neq__(self,other):
		return not self.__eq__(other)

	def __round_to_n(self, x,n = 6):
		if x == 0.0:
			return 0
		else:
			return round(float(x), -int(floor(log10(abs(float(x))))) + (n - 1))

	def __str__(self):
		"Pretty print"
		if self.unit != None:
			return "("+str(self.__round_to_n(self.x))+","+str(self.__round_to_n(self.y))+" " +self.unit + ")"
		else:
			return "("+str(self.__round_to_n(self.x))+","+str(self.__round_to_n(self.y))+")"



zeroVector = Vector2D(0.0,0.0)
