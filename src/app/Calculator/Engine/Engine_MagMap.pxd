from .Engine cimport Engine
import numpy as np

cdef class Engine_MagMap(Engine):

	cdef public object magMapParameters
	cdef public object magMapArray
	cdef Engine __internalEngine

	cdef unsigned int query_data_length(self, double x, double y, double radius) nogil
	cdef makeLightCurve_helper(self, object mmin, object mmax, int resolution)