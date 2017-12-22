

from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair

cdef extern from "WindowGrid.hpp":
	cdef cppclass WindowGrid[Grid]:
		WindowGrid(double*, double*,int, int, int) nogil
		WindowGrid() except +
		vector[pair[int,int]] find_within(double,double,double) nogil
		bool translate_window_to(pair[double,double] dimensions) nogil
		bool reshape_window_to(pair[double,double] dimensions) nogil
		bool set_corners(pair[double,double] tl, pair[double,double] br) nogil
		int find_within_count(double,double,double) nogil
		bool clear() except +
		int size() except +
		