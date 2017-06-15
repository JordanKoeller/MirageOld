

from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair

cdef extern from "PointerGrid.hpp":
	cdef cppclass PointerGrid:
		PointerGrid(double*, double*,int, int, int, int) nogil
		PointerGrid() except +
		vector[pair[int,int]] find_within(double,double,double) nogil
		bool clear() except +
		