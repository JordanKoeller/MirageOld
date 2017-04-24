

from libcpp.vector cimport vector
from libcpp cimport bool
from libcpp.pair cimport pair

cdef extern from "Grid.hpp":
	cdef cppclass Pixel:
		double x
		double y
		int pixelX
		int pixelY
		Pixel() except +
		Pixel(double,double,int, int) except +
	cdef cppclass Grid:
		Grid(double, double,double,double,int) except +
		Grid() except +
		Grid(vector[pair[pair[double,double],pair[int,int]]].iterator,vector[pair[pair[double,double],pair[int,int]]].iterator,int)		
		vector[Pixel] find_within(double,double,double) except +
		bool insert(double,double, int, int) except +
		bool clear() except +

