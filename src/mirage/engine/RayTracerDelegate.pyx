
from libc.math cimport sin, cos, atan2, sqrt, pi
import numpy as np
cimport numpy as np
import cython
@cython.boundscheck(False)
@cython.wraparound(False)
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
                ):
    cdef double pi2 = pi/2
    cdef int i, x, y
    cdef double deltaR_x, deltaR_y, r, incident_angle_x, incident_angle_y, phi
    cdef int numStars = len(stars)
    cdef int xmax = len(inputCoords)
    cdef int ymax = len(inputCoords[0])
    with nogil:
        for x in range(xmax):
            for y in range(ymax):
                incident_angle_x = inputCoords[x,y,0] * dTheta
                incident_angle_y = inputCoords[x,y,1] * dTheta
                inputCoords[x,y,0] = 0.0
                inputCoords[x,y,1] = 0.0

                for i in range(numStars):
                    deltaR_x = incident_angle_x - stars[i,0]
                    deltaR_y = incident_angle_y - stars[i,1]
                    r = deltaR_x * deltaR_x + deltaR_y * deltaR_y
                    if r != 0.0:
                        inputCoords[x, y,0] += deltaR_x * stars[i,2] * point_constant / r;
                        inputCoords[x, y,1] += deltaR_y * stars[i,2] * point_constant / r;                
    #                 
                # SIS
                deltaR_x = incident_angle_x - centerX
                deltaR_y = incident_angle_y - centerY
                r = sqrt(deltaR_x * deltaR_x + deltaR_y * deltaR_y)
                if r != 0.0:
                    inputCoords[x, y,0] += deltaR_x * sis_constant / r 
                    inputCoords[x, y,1] += deltaR_y * sis_constant / r

                # Shear
                phi = 2 * (pi2 - shearAngle) - atan2(deltaR_y, deltaR_x)
                inputCoords[x, y,0] += shearMag * r * cos(phi)
                inputCoords[x, y,1] += shearMag * r * sin(phi)
                inputCoords[x, y,0] = deltaR_x - inputCoords[x, y,0]
                inputCoords[x, y,1] = deltaR_y - inputCoords[x, y,1]



def ray_trace(inputCoords, parameters):
    import math
    from astropy import constants as const
    dS = parameters.quasar.angDiamDist.to('lyr').value
    dL = parameters.galaxy.angDiamDist.to('lyr').value
    dLS = parameters.dLS.to('lyr').value
    stars = parameters.stars
    _ray_trace(stars,
              inputCoords,
              (4*(const.G/const.c/const.c).to('lyr/solMass').value*dLS/dS/dL),
              (4*math.pi*parameters.galaxy.velocityDispersion**2*(const.c**-2).to('s2/km2').value*dLS/dS).value,
              parameters.galaxy.shear.magnitude,
              parameters.galaxy.shear.angle.to('rad').value,
              parameters.dTheta.to('rad').value,
              parameters.galaxy.position.to('rad').x,
              parameters.galaxy.position.to('rad').y
              )
    return inputCoords