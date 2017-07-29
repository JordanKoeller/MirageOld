cimport numpy as np
import numpy as np
from .Drawer cimport Drawer

cdef class CurveDrawer_Tracer(Drawer):
    cdef np.float64_t[:] xAxis
    cdef np.float64_t[:] yAxis
    cdef int index
    cdef append(self, double y, double x=*)
    cdef plotAxes(self, np.ndarray[np.float64_t, ndim=1] x, np.ndarray[np.float64_t, ndim=1] y)