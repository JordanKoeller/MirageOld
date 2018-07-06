import numpy as np
cimport numpy as np

cdef void _ray_trace(
                np.ndarray[np.float64_t, ndim = 2] stars, #x,y,m
                np.ndarray[np.float64_t, ndim = 3] inputCoords,
                double point_constant,
                double sis_constant,
                double shearMag,
                double shearAngle,
                double dTheta,
                double centerX,
                double centerY
                )

# def ray_trace(inputCoords, parmeters)