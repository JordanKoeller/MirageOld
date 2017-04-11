import numpy as np
from Utility import Vector2D
from Utility import zeroVector
class Plot(object):
	"""docstring for Plot"""
	def __init__(self,span):
		super(Plot, self).__init__()
		self.span = span
		self.canvas = np.zeros((self.span.x+1,self.span.y+1),dtype = np.uint8)
		self.xAxis = np.zeros(self.span.x)
		self.yAxis = np.zeros(self.span.y)
		self.operatingIndex = 0
		self.yExtremes = Vector2D(0,10)
		self.colorCode = 1
		self.__normalizeRange(np.array([0,1]))
		# self.__normalizeRange(self.yAxis)
		
	# def plotToArray(self,dataX,dataY,colorCode=1):
	# 	if len(dataX) != len(dataY):
	# 		print("ERROR: X and Y values must be of the same shape[0] and dimension.")
	# 		return
	# 	maxx = (max(dataX),max(dataY))
	# 	minn = (min(dataX),min(dataY))
	# 	normalizedX = (dataX - minn[0]) * (self.span.x - self.leftCorner.x - 1) / (maxx[0] - minn[0])
	# 	normalizedY = (dataY - minn[1]) * (self.span.y - self.leftCorner.y - 1) / (maxx[1] - minn[1])
	# 	for i in range(0,len(normalizedX)):
	# 		intX = int(self.leftCorner.x + normalizedX[i])
	# 		intY = int((self.span.y-1) - normalizedY[i])
	# 		self.canvas[intX,intY] = colorCode
	# 	self.yExtremes = Vector2D(minn[1],maxx[1])
	# 	return self.canvas


	def __normalizeRange(self,y):
		ret = (y+self.yExtremes.x)*(self.span.y-1)/(self.yExtremes.y - self.yExtremes.x)
		return ret

	def __rescaleX(self):
		tmp = self.yAxis
		# print("Rescaling")
		# print(self.operatingIndex)
		# print("with shaepe")
		# print(self.yAxis.shape[0])
		self.yAxis = np.zeros(self.yAxis.shape[0]*3)
		for i in range(0,tmp.shape[0]):
			self.yAxis[i] = tmp[i]
			# self.__interpolateBtPoints(self.canvas,tmp[i],tmp[i+1],i)

	def __plotArray(self,data):
		self.canvas = np.zeros((self.span.x,self.span.y),dtype=np.uint8)
		for i in range(0,self.yAxis.shape[0]-1):
			if int(self.yAxis[i]) != 0:
				x1 = i 
				x2 = i+1 
				y1 = data[i]
				y2 = data[i+1]
				self.__drawLine(x1,x2,y1,y2)
				# index = self.operatingIndex*self.span.x/self.yAxis.shape[0] - 1
				# self.canvas[index,self.span.y-int(data[i])] = 1

	def appendYValue(self,y):
		if self.operatingIndex  >= self.yAxis.shape[0]:
			self.__rescaleX()
		self.yAxis[self.operatingIndex] = y
		if y > self.yExtremes.y or y < self.yExtremes.x:
			if y > self.yExtremes.y:
				self.yExtremes.y = y
			else:
				self.yExtremes.x = y
			data = self.__normalizeRange(self.yAxis)
			self.__plotArray(data)
		normVal = self.__normalizeRange(y)
		# print(normVal)
		index = self.operatingIndex*self.span.x/self.yAxis.shape[0] - 1
		y1 = self.__normalizeRange(self.yAxis[self.operatingIndex-1])
		y2 = normVal
		x1 = self.operatingIndex-1
		x2 = self.operatingIndex
		self.__drawLine(x1,x2,y1,y2)
		self.canvas[index,self.span.y - int(normVal) - 1] = self.colorCode
		self.operatingIndex += 1

	def test_bounds(self,canvas):
		for i in range(self.leftCorner.y,self.span.y-1):
			canvas[self.leftCorner.x,i] = 1
			canvas[self.span.x-1,i] = 1
		for i in range(self.leftCorner.x,self.span.x-1):
			canvas[i,self.leftCorner.y] = 1
			canvas[i,self.span.y - 1] = 1
		return canvas

	def __drawLine(self,x1,x2,y1,y2):
		m = (y2-y1)/(x2-x1)
		if y2-y1 > x2-x1:
			# print("iterating on y")
			for i in range(0,int(y2-y1)):
				x = i/m + x1
				y = self.span.y - (i + y1 + 0.5)
				# print(str(x)+","+str(y))
				if x >= 0 and x < self.span.x and y >= 0 and y < self.span.y:
					self.canvas[int(x),int(y)] = 1
		else:
			for i in range(0,int(x2-x1)):
				x = x1+i + 0.5
				y = self.span.y - (y1 + m*i + 0.5)
				if x >= 0 and x < self.span.x and y >= 0 and y < self.span.y:
					self.canvas[int(x),int(y)] = 1
# dy = mx 
# dy/m = x




def test():
	canvas = np.zeros((100,100),dtype=np.uint8)
	p = Plot(canvas)
	return p
	# def plotPair(self,x,y,canvas,colorCode=1):
	# 	nx = (x /self.span.x) 
