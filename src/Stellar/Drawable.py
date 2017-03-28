from Utility.Vector2D import zeroVector


class Drawable(object):
	__position = zeroVector
	__colorKey = 0

	def draw(self, img, parameters):
		"""Draws the entity to the canvas.
		Args:
			img - QImage to be drawn to.
			parameters - Configs class instance, specifying how to draw the entity.
		"""

	# def updateDrawable(self, position = None, colorKey = None):
	# 	if position != None:
	# 		self.__position = position
	# 	if colorKey != None:
	# 		self.__colorKey = colorKey

	def updateDrawable(self,**kwargs):
		for key,value in kwargs.items():
			try:
				getattr(self,"_Drawable__"+key)
				if value != None:
					setattr(self,"_Drawable__"+key,value)
			except AttributeError as e:
				print("failed to update "+key+ " in Drawable")


	def setPos(self,position):
		self.__position = position

	@property
	def position(self):
		return self.__position

	@property
	def colorKey(self):
		return self.__colorKey

	def drawableString(self):
		return "postion = " + str(self.position)