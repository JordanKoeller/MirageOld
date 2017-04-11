class FrameDrawer(object):
	"""docstring for FrameDrawer"""
	def __init__(self,*args):
		super(FrameDrawer, self).__init__()
		self.args = args

	def draw(self,parameters,canvas): #Where "canvas is a np array"
		for i in self.args:
			i.draw(parameters,canvas)
		return canvas

		
def FrameDrawerFactory(parameters, lightCurveFrame, imageFrame):
	drawer = FrameDrawer()