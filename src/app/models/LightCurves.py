import numpy as np
from app.utility import Vector2D
from astropy import units as u

class LightCurveBatch(object):
	def __init__(self,lightcurve_array):
		self._data = lightcurve_array

	def plottables(self,unit='uas'):
		for curve in self:
			xAxis = curve.distance_axis.to(unit)
			yAxis = curve.curve 
			yield (xAxis,yAxis)

	def __getitem__(self,ind):
		if isinstance(ind,int):
			if ind < len(self):
				data = self._data[ind]
				counts,queries = data
				return LightCurve(counts,queries)
			else:
				raise IndexError("Index out of range.")
		elif isinstance(ind,slice):
			return LightCurveBatch(self._data[ind])
		else:
			raise ValueError("Could not understand ind as an index or slice.")

	def __len__(self):
		return self._data.shape[0]

class LightCurve(object):
	def __init__(self,data,query_points):
		self._data = data.flatten()
		start = query_points[0]
		end = query_points[-1]
		self._start = Vector2D(start[0],start[1],'rad')
		self._end = Vector2D(end[0],end[1],'rad')

	def __len__(self):
		return len(self._data)

	@property
	def curve(self):
		return self._data

	@property
	def query_points(self):
		x = np.linspace(self._start.x,self._end.x,len(self))
		y = np.linspace(self._start.y,self._end.y,len(self))
		ret = np.ndarray((len(x),2))
		ret[:,0] = x
		ret[:,1] = y
		return u.Quantity(ret,'rad')

	@property
	def distance_axis(self):
		qpts = self.query_points.value
		x = qpts[:,0]
		y = qpts[:,1]
		xs = x[0]
		ys = y[0]
		diffx = x -xs
		diffy = y - ys
		res = (diffx**2+diffy**2)**(0.5)
		return u.Quantity(res,'rad')

	def plottable(self,unit='uas'):
		x = self.distance_axis.to(unit)
		y = self.curve
		return (x,y)
	


	def __getitem__(self,given):
		if isinstance(given,slice):
			qpts = self.query_points
			return LightCurve(self.curve[given],qpts[given])
		else:
			raise TypeError("Must give a valid slice object")
