from ...Utility import zeroVector
from ..ParametersError import ParametersError

class Drawable(object):
	__position = zeroVector
	__colorKey = 0
	
	def __init__(self):
		pass

	def draw(self, img, parameters):
		"""Draws the entity to the canvas.
		Args:
			img - QImage to be drawn to.
			parameters - Configs class instance, specifying how to draw the entity.
		"""

	def updateDrawable(self,**kwargs):
		for key,value in kwargs.items():
			try:
				getattr(self,"_Drawable__"+key)
				if value != None:
					setattr(self,"_Drawable__"+key,value)
			except AttributeError as e:
				raise ParametersError("failed to update "+key+ " in Drawable")


	def setPos(self,position):
		self.__position = position

	@property
	def position(self):
		return self.__position.to('rad')

	@property
	def colorKey(self):
		return self.__colorKey

	def drawableString(self):
		return "postion = " + str(self.position)