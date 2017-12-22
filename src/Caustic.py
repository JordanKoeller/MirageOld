import numpy as np
import math

class Rectangle(object):
	"""Class used to describe a rectangular source object.
	rectangles with the same group value will displayed on one curve.
	size describes the size of the rectangle, relative to the size of the cuastic crossing.
	shift represents a linear shift away from the default situation of the rectangle crossing the caustic at x = 0.0"""
	def __init__(self,group, sz=1.0,shift=0.0):
		self.s = sz
		self.shift = shift
		self.group = group



def plotCaustic(s,xMin=-4.0,xMax=4.0):
	"Plot a single caustix event. xMin and xMax define the domain of the plot."
	d = 1.0
	xVals = np.arange(xMin,xMax,0.01)
	yVals = np.arange(xMin,xMax,0.01)
	for z in np.nditer(yVals, op_flags=['readwrite']):
		if s/d/2 < z:
			z[...] = 4*(d/s)*(math.sqrt(z/d+s/d/2)-math.sqrt(z/d-s/d/2))
		elif -s/d/2 < z and s/d/2 > z:
			z[...] = 4*(d/s)*math.sqrt(z/d+s/d/2)
		else:
			z[...] = 0.0
	return (xVals,yVals)			

# def plotCaustics(rects,xMin = -4.0, xMax = 4.0):
# 	"""Plots a list of Rectangle objects withing one figure.
# 	xMin and xMax define the domain of the plot."""
# 	class Node(object):
# 		def __init__(self,yVals,rect):
# 			self.rects = []
# 			self.yVals = yVals
# 			self.rects.append(rect)
# 	d = 1.0
# 	xVals = np.arange(xMin,xMax,0.01)
# 	sz = len(xVals)
# 	gps = {}
# 	for i in rects:
# 		if i.group not in gps:
# 			gps[i.group] = Node(np.zeros(sz),i)
# 		else:
# 			gps[i.group].rects.append(i)

# 	for gp in gps.values():
# 		for rect in gp.rects:
# 			for i in range(sz):
# 				s = rect.s
# 				z = xVals[i]-rect.shift
# 				if s/d/2 < z:
# 					gp.yVals[i] = 4*(d/s)*(math.sqrt(z/d+s/d/2)-math.sqrt(z/d-s/d/2)) + gp.yVals[i]
# 				elif -s/d/2 < z and s/d/2 > z:
# 					gp.yVals[i] = 4*(d/s)*math.sqrt(z/d+s/d/2) + gp.yVals[i]
# 				else:
# 					gp.yVals[i] = 0.0 + gp.yVals[i]





# def plotAnnular(s,s2,xMin = -4.0, xMax = 4.0):
# 	"""Plots two caustics with sizes of s and s2 in an annular fashion.
# 		Assumes s2 is larger than s.
# 		xMin and xMax describe the domain of the plot."""
# 	assert s2 > s
# 	d = 1.0
# 	xVals = np.arange(xMin,xMax,0.01)
# 	yValsSm = np.arange(xMin,xMax,0.01)
# 	yValsLg = np.arange(xMin,xMax,0.01)

# 	for z in np.nditer(yValsSm, op_flags=['readwrite']):
# 		if s/d/2 < z:
# 			z[...] = 4*(d/s)*(math.sqrt(z/d+s/d/2)-math.sqrt(z/d-s/d/2))
# 		elif -s/d/2 < z and s/d/2 > z:
# 			z[...] = 4*(d/s)*math.sqrt(z/d+s/d/2)
# 		else:
# 			z[...] = 0.0

# 	for z in np.nditer(yValsLg, op_flags=['readwrite']):
# 		if s2/d/2 < z:
# 			z[...] = 4*(d/s2)*(math.sqrt(z/d+s2/d/2)-math.sqrt(z/d-s2/d/2))
# 		elif -s2/d/2 < z and s2/d/2 > z:
# 			z[...] = 4*(d/s2)*math.sqrt(z/d+s2/d/2)
# 		else:
# 			z[...] = 0.0

# 	for i in range(len(xVals)):
# 		yValsLg[i] = yValsLg[i] - yValsSm[i]

