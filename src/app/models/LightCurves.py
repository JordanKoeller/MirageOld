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

class LightCurveClassificationTable(LightCurveBatch):

	def __init__(self,curves,p_value_threshold=0.2,method='craimer',*args,**kwargs):
		LightCurveBatch.__init__(self,curves,*args,**kwargs)
		if method == 'craimer':
			self._chooser = CraimerChooser()
		elif method == 'KS':
			self._chooser = KSChooser()
		elif method == 'MannWhitney':
			self._chooser = MannWhitneyChooser()
		self._p_threshold = p_value_threshold
		self._table = [[]]


	def get_classification(self,curve):
		"""Method that gives a "dry-run" classification, saying the index in the table
		that the value falls into, or if it is unique and warrants a new classification be added.
		
		
		Arguments:
			curve {:class:`LightCurve`} -- The light curve to classify.

		Returns:
			unique {`bool`} -- If true, no curve was found that is similar to `curve`
				inside the :class:`LightCurveClassificationTable` instance.
			classification_id {`into`} -- The index in the table where this curve would
			be inserted.
		"""
		best_p = self._p_threshold
		best_I = -1
		for curve_typeI in self.category_count:
			representative = self.get_representative_curve(curve_typeI)
			p_value = self._chooser.choose(curve,representative)
			if p_value < best_p:
					best_p = p_value
					best_I = curve_typeI
		if best_I == -1:
			return (False, self.category_count)
		else:
			return (True, best_I)

	@property
	def category_count(self):
		return len(self._table)

	def describe(self):
    	for i in range(len(self._table)):
        	print("Group " + str(i) + " with " + str(len(table[i])) + " elements.")

	def get_representative_curve(cat_ind:int) -> LightCurve:
		if len(self._table) <= cat_ind:
			raise IndexError("curve group " + str(cat_ind) + "does not exist out of the " + str(len(self._table)) + " tabulated curve groups")
		else:
			rand_elem = random.randint(0,len(self._table[cat_ind]))
			return self._table[cat_ind][rand_elem]

	def __getitem__(self,ind):
		if ind < self.category_count:
			return LightCurveBatch(self._table[ind])
		else:
			raise IndexError("curve group " + str(ind) + "does not exist out of the " + str(len(self._table)) + " tabulated curve groups")

	def __len__(self):
		counter = 0
		for i in table:
			counter += len(i)
		return counter

		

class Chooser(ABC):

	self.__init__(self):
		pass

	@abstractmethod
	def choose(self,a:LightCurve,b:LightCurve) -> float:
		'''Compares the light curves `a` and `b` and returns the p-value of their similarity.
		
		Abstract method, that must be overriden by :class:`Chooser` sub-classes.
		
		Arguments:
			a {:class:`LightCurve} -- The light curve to compare to curve `b`
			b {:class:`LightCurve`} -- The reference curve for comparison.

		Returns:
			p_value {`float`} -- The p-value ranking for similarity between the two curves. 
			A lower p-value represents curves that are more similar to each other.
		'''
		pass

class CraimerChooser(Chooser):

	def __init__(self):
		Chooser.__init__(self)


	def choose(self,a:LightCurve,b:LightCurve) -> float:
		from scipy.stats import energy_distance
		c1 = a.curve
		c2 = b.curve
		return energy_distance(c1,c2)
