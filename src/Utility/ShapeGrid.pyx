from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair
cdef extern from "ShapeGrid.hpp":
	cdef cppclass ShapeGrid:
		ShapeGrid(double*,double*, int, int, int, int) nogil
		ShapeGrid() except +
		vector[pair[int,int]] find_within(double,double,double) nogil
		bool clear() except +