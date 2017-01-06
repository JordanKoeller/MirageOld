# distutils: language=c++
# cython: profile=True


from libcpp.vector cimport vector
from libcpp cimport bool

# STUFF = "Hi"

cdef extern from "SpatialTree_new.h":
	cdef cppclass Pixel:
		int x
		int y
		Pixel() except +
		Pixel(int, int) except +
	cdef cppclass SpatialTree:
		SpatialTree() except +
		SpatialTree(double, double, double, double) except +
		bool insert(int, int, double, double)
		int size()
		int getEmptyCount()
		int getNodeCount()
		void trimTree()
		vector[Pixel] query_point(double,double,double) except +
		SpatialTree &operator=(SpatialTree) except +
