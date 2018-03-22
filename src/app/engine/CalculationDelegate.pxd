cdef class CalculationDelegate:

    cdef object _parameters

    cpdef void reconfigure(self,object parameters)
    
    cpdef object make_light_curve(self,object mmin, object mmax, int resolution)
    
    cpdef object make_mag_map(self,object center, object dims, object resolution)
    
    cpdef object get_frame(self,object x, object y, object r)
    
    cdef ray_trace(self)
    
    cpdef unsigned int query_data_length(self, object x, object y, object radius)
    
    
