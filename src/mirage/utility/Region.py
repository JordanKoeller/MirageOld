from .Vec2D import Vector2D
from .JSON import JSONable

from astropy import units as u

class Region(JSONable):

	"""Defines a region of space.
	
	The region is rectangular, with a center and dimensions specified.
	""" 

	def __init__(self,center:Vector2D, dims:Vector2D) -> None:
		self._center = center
		self._dims = dims


	@property
	def center(self) -> Vector2D:
		return self._center

	@property
	def dimensions(self) -> Vector2D:
		return self._dims

	@property
	def area(self) -> u.Quantity:
		return self.dimensions.x*self.dimensions.y*self.dimensions.unit*self.dimensions.unit

	def json_helper(self) -> dict:
		ret = {}
		ret['center'] = self.center.json
		ret['dims'] = self.dimensions.json
		return ret
		

	@property
	def json(self) -> dict:
		return self.json_helper()

	@classmethod
	def from_json(cls,js):
		center = Vector2D.from_json(js['center'])
		dims = Vector2D.from_json(js['dims'])
		return cls(center,dims)
	
class PixelRegion(Region):

	def __init__(self,center:Vector2D,dims:Vector2D,grid_resolution:Vector2D) -> None:
		Region.__init__(self,center,dims)
		print(grid_resolution)
		self._dtheta = dims/grid_resolution

	@property
	def dTheta(self) -> Vector2D:
		return self._dtheta

	@property
	def resolution(self):
		return (self.dimensions/self.dTheta).unitless()


	def loc_to_pixel(self,loc:Vector2D) -> Vector2D:
		delta = loc - self.center
		pixellated = delta.to(self.dTheta.unit)/self.dTheta
		return Vector2D(int(pixellated.x),int(pixellated.y))

	def pixel_to_loc(self,pixel:Vector2D) -> Vector2D:
		delta = pixel * self.dTheta
		return delta + self.center.to(delta.unit)


	@property
	def json(self):
		ret = Region.json_helper(self)
		ret['resolution'] = self.resolution.json
		return ret

	@classmethod
	def from_json(cls,js):
		center = Vector2D.from_json(js['center'])
		dims = Vector2D.from_json(js['dims'])
		resolution = Vector2D.from_json(js['resolution'])
		return cls(center,dims,resolution)



