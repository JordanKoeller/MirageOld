from __future__ import division

from .CalculationDelegate cimport CalculationDelegate
from libcpp cimport bool
from mirage.utility.PointerGrid cimport PointerGrid
from libcpp.pair cimport pair
from libcpp.vector cimport vector
import numpy as np 
cimport numpy as np

cdef class PointerGridCalculationDelegate(CalculationDelegate):

    cdef PointerGrid __grid
    cdef bool needsReconfiguring
    cdef int core_count
    cdef public double time
    cdef bool __preCalculating

#     cdef void reconfigure(self,object parameters)
#     
#     cdef object make_light_curve(self,object mmin, object mmax, int resolution)
#     
#     cdef object make_mag_map(self,object center, object dims, object resolution)
#     
#     cdef object get_frame(self,object x, object y, object r)
#     
#     cdef void ray_trace(self)
#     
#     cdef unsigned int query_data_length(self, object x, object y, object radius)
    
    
    #PointerGrid specific methods
    cdef vector[pair[int,int]] query_data(self, double x, double y, double radius) nogil
    cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray,int binsize)
  
    
