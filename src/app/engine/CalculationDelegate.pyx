cdef class CalculationDelegate:

    def __init__(self):
        self._parameters = None

    cpdef void reconfigure(self,object parameters):
        raise NotImplementedError
    
    cpdef object make_light_curve(self,object mmin, object mmax, int resolution):
        raise NotImplementedError
    
    cpdef object make_mag_map(self,object center, object dims, object resolution):
        raise NotImplementedError
    
    cpdef object get_frame(self,object x, object y, object r):
        raise NotImplementedError
    
    cpdef ray_trace(self):
        raise NotImplementedError
    
    cpdef unsigned int query_data_length(self, object x, object y, object radius):
        raise NotImplementedError


# For regular python extensions, below is a template:


# class MagMapCalculationDelegate(CalculationDelegate):
#     '''
#     classdocs
#     '''
# 
# 
#     def __init__(self):
#         '''
#         Constructor
#         '''
#         CalculationDelegate.__init__(self)
# 
#     def reconfigure(self,parameters):
#         raise NotImplementedError
#     
#     def make_light_curve(self,mmin, mmax, resolution):
#         raise NotImplementedError
#     
#     def make_mag_map(self,center, dims, resolution):
#         raise NotImplementedError
#     
#     def get_frame(self,x, y, r):
#         raise NotImplementedError
#     
#     def ray_trace(self):
#         raise NotImplementedError
#     
#     def int query_data_length(self, x, y, radius):
#         raise NotImplementedError