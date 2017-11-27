from __future__ import division

from pyspark import SparkContext
import numpy as np
cimport numpy as np
from .Engine cimport Engine
from libc cimport math as CMATH

from astropy import constants as const

sc = SparkContext('local','test')
sc.setLogLevel('WARN')

_width = 2000
_height = 2000
_b = []

def _reconfigure(self):
    _width = self.parameters.canvasDim
    _height = self.parameters.canvasDim
    #First, set up some functions for mapping over:

    def _mk_ray(index):
        return _Ray(index // _width, index % _width)
    int_RDD = sc.range(_width*_height)
    rayList_RDD = int_RDD.map(_mk_ray).glom()
    dS = self.parameters.quasar.angDiamDist.to('lyr').value
    dL = self.parameters.galaxy.angDiamDist.to('lyr').value
    dLS = self.parameters.dLS.to('lyr').value
    args = (self.parameters.stars,
                len(self.parameters.stars),
                4*(const.G/const.c/const.c).to('lyr/solMass').value*dLS/dS/dL,
                4*CMATH.pi*self.parameters.galaxy.velocityDispersion*2*(const.c**-2).to('s2/km2').value*dLS/dS,
                self.parameters.galaxy.shear.magnitude,
                self.parameters.galaxy.shear.angle.to('rad').value,
                _width,
                _height,
                self.parameters.dTheta.to('rad').value,
                self.parameters.galaxy.position.to('rad').x,
                self.parameters.galaxy.position.to('rad').y
                )
    _b = sc.broadcast(args) #Broadcasted arguments



    def _ray_trace(pixels):
        return _ray_trace_helper(pixels,_b[0],_b[1],_b[2],_b[3],_b[4],_b[5],_b[6],_b[7],_b[8],_b[9],_b[10])

    ray_traced_RDD = rayList_RDD.map(_ray_trace)
        
    ray_traced_RDD.collect()
    print("FINSIHED RAY TRACING AND MAPPING")
        


cpdef _ray_trace_helper(object pixels, #MAY NEED TO BE A CPDEF, BUT TRY THIS FIRST
                       np.ndarray[np.float64_t,ndim=2] stars,
                       int num_stars,
                       double point_constant,
                       double sis_constant,
                       double shear_mag,
                       double shear_angle,
                       int width,
                       int height,
                       double dTheta,
                       double centerX,
                       double centerY):
    cdef int x,y,i
    cdef double pi2 = CMATH.pi/2.0
    cdef double incident_angle_x, incident_angle_y, r, delta_x, delta_y, phi
    cdef np.ndarray[np.float64_t,ndim=3] incident_pixel = np.ndarray((width,height,2))
    cdef np.ndarray[np.float64_t,ndim=3] result_array = np.ndarray((width,height,2))
    for x in range(0,width):
        for y in range(0, height):
            incident_pixel[x,y] = [pixels[x*width+y].x,pixels[x*width+y].y]
    height = height//2
    width = width//2
    for x in range(0,width):
        for y in range(0, height):
            incident_angle_x = (incident_pixel[x,y,0] - width)*dTheta
            incident_angle_y = (height - [x,y,1])*dTheta

        for i in range(num_stars):
            deltaR_x = incident_angle_x - stars[i,0]
            deltaR_y = incident_angle_y - stars[i,1]
            r = deltaR_x*deltaR_x + deltaR_y*deltaR_y
            if r != 0.0:
                result_array[x,y,0] += deltaR_x*stars[i,2]*point_constant/r;
                result_array[x,y,1] += deltaR_y*stars[i,2]*point_constant/r;       
       
        #SIS
        deltaR_x = incident_angle_x - centerX
        deltaR_y = incident_angle_y - centerY
        r = CMATH.sqrt(deltaR_x*deltaR_x+deltaR_y*deltaR_y)
        if r != 0.0:
            result_array[x,y,0] += deltaR_x*sis_constant/r 
            result_array[x,y,1] += deltaR_y*sis_constant/r

        #Shear
        phi = 2*(pi2 - shear_angle )-CMATH.atan2(deltaR_y,deltaR_x)
        result_array[x,y,0] += shear_mag*r*CMATH.cos(phi)
        result_array[x,y,1] += shear_mag*r*CMATH.sin(phi)
        result_array[x,y,0] = deltaR_x - result_array[x,y,0]
        result_array[x,y,1] = deltaR_y - result_array[x,y,1]
    for x in range(0,width*2):
        for y in range(0, height*2):
            pixels[x*width+y] = _Ray(x,y,result_array[x,y,0],result_array[x,y,1])
    return pixels

cdef class _Ray:

    cdef int pixel_x
    cdef int pixel_y
    cdef double spp_x
    cdef double spp_y

    def __init__(self,int x,int y, double sx = 0.0, double sy = 0.0):
        self.pixel_x = x
        self.pixel_y = y
        self.spp_x = x #spp = Source Plane Position
        self.spp_y = y


cdef class Engine_Spark(Engine):
    '''
    Class for ray-tracing and getting magnification maps from the cluster. Similar to the Engine class but for parallel execution.
    '''

    def __cinit__(self):
        pass


    
    def reconfigure(self):
        _reconfigure(self)

