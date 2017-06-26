

from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair

cdef extern from "PointerGrid.hpp":
	cdef cppclass PointerGrid:
		PointerGrid(double*,double*, int, int, int, int) nogil
		PointerGrid() except +
		pair[vector[pair[int,int]],double] find_within(double,double,double) nogil
		bool clear() except +
		
		