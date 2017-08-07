from .Engine cimport Engine
from ...Utility.Vec2D import Vector2D
import numpy as np

cdef class Engine_MagMap(Engine):
	"""Engine for querying an array of magnification map data. Allows for the same interface whether dealing with pre-generated
	data or on-the-fly data."""
	def __init__(self, parameters, magMapParameters, magMapArray):
		Engine.__init__(self,parameters)
		self.magMapParameters = magMapParameters
		self.magMapArray = magMapArray


	def reconfigure(self):
		if self.__internalEngine:
			self.__internalEngine.reconfigure()


	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil:
		with gil:
			if self.__internalEngine:
				return self.__internalEngine.query_data_length(x,y,radius)
			else:
					pixels = self.magMapParameters.angleToPixel(Vector2D(x,y))
					ret = self.magMapArray[round(pixels.x),round(pixels.y)]
					return <unsigned int> ret*self.trueLuminosity

	cdef makeLightCurve_helper(self, object mmin, object mmax, int resolution):
		"""Deprecated"""

		if self.__internalEngine:
			return self.__internalEngine.makeLightCurve_helper(mmin,mmax,resolution)
		else:
			pixelStart = self.magMapParameters.angleToPixel(mmin)
			pixelEnd = self.magMapParameters.angleToPixel(mmax)
			dx = pixelEnd.x - pixelStart.x
			dy = pixelEnd.y - pixelStart.y
			maxD = max(dx,dy)
			xSteps = np.arange(pixelStart.x,pixelEnd.x,dx/maxD)
			ySteps = np.arange(pixelStart.y,pixelEnd.y,dy/maxD)
			xPixels = self.magMapParameters.pixelToAngle(xSteps)
			yPixels = self.magMapParameters.pixelToAngle(ySteps)
			retArr = np.ones_like(xSteps,dtype=np.float64)
			for index in range(len(retArr)):
				value = self.magMapArray[round(xPixels[index]),round(yPixels[index])]
				retArr[index] = value
			return retArr
