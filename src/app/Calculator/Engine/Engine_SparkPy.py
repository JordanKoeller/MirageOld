from __future__ import division

from pyspark import SparkContext, SparkConf
import numpy as np
import math as CMATH
from .Engine import Engine
from astropy import constants as const

conf = SparkConf().setAppName("App")
conf = (conf.setMaster('local[*]')
        .set('spark.executor.memory', '4G')
        .set('spark.driver.memory', '4G')
        .set('spark.driver.maxResultSize', '4G'))
sc = SparkContext(conf=conf)
sc.setLogLevel('WARN')


def _ray_trace_helper(pixels, #MAY NEED TO BE A CPDEF, BUT TRY THIS FIRST
                       stars,
                       num_stars,
                       point_constant,
                       sis_constant,
                       shear_mag,
                       shear_angle,
                       width,
                       height,
                       dTheta,
                       centerX,
                       centerY):
    pi2 = CMATH.pi/2.0
    slice_length = len(pixels)
    incident_pixel = np.ndarray((slice_length,2))
    result_array = np.ndarray((slice_length,2))
    for i in range(0, slice_length):
        incident_pixel[i] = [pixels[i].pixel_x,pixels[i].pixel_y]
    for i in range(0, slice_length):
        incident_angle_x = (incident_pixel[i,0] - width/2)*dTheta
        incident_angle_y = (height - incident_pixel[i,1]/2)*dTheta
        for j in range(num_stars):
            deltaR_x = incident_angle_x - stars[j,0]
            deltaR_y = incident_angle_y - stars[j,1]
            r = deltaR_x*deltaR_x + deltaR_y*deltaR_y
            if r != 0.0:
                result_array[i,0] += deltaR_x*stars[j,2]*point_constant/r;
                result_array[i,1] += deltaR_y*stars[j,2]*point_constant/r;       
       
        #SIS
        deltaR_x = incident_angle_x - centerX
        deltaR_y = incident_angle_y - centerY
        r = CMATH.sqrt(deltaR_x*deltaR_x+deltaR_y*deltaR_y)
#        if r != 0.0:
#            result_array[i,0] += deltaR_x*sis_constant/r 
#            result_array[i,1] += deltaR_y*sis_constant/r

        #Shear
        phi = 2*(pi2 - shear_angle )-CMATH.atan2(deltaR_y,deltaR_x)
        result_array[i,0] += shear_mag*r*CMATH.cos(phi)
        result_array[i,1] += shear_mag*r*CMATH.sin(phi)
        result_array[i,0] = deltaR_x - result_array[i,0]
        result_array[i,1] = deltaR_y - result_array[i,1]
    return result_array

class _Ray(object):


    def __init__(self,x,y,sx = 0.0,sy = 0.0):
        self.pixel_x = x
        self.pixel_y = y
        self.spp_x = x #spp = Source Plane Position
        self.spp_y = y


class Engine_Spark(Engine):
    '''
    Class for ray-tracing and getting magnification maps from the cluster. Similar to the Engine class but for parallel execution.
    '''

    def __init__(self,rdd_grid):
        self._rdd_grid = rdd_grid

    
    def reconfigure(self):
        _width = self.parameters.canvasDim
        _height = self.parameters.canvasDim
        #First, set up some functions for mapping over:

        int_RDD = sc.range(_width*_height)
        rayList_RDD = int_RDD.map(lambda index: _Ray(index // _width, index % _width)).glom()
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
        ray_traced_RDD = rayList_RDD.map(lambda pixels: _ray_trace_helper(pixels,*(_b.value)))
        
        # ray_traced_RDD.collect()
        self._grid = self._rdd_grid.construct(ray_traced_RDD)
        print("FINSIHED RAY TRACING AND MAPPING")
        
    def makeMagMap(self, center, dims, resolution,*args,**kwargs):
        '''
        Calulates and returns a 2D magnification map of the magnification coefficients 
        of a quasar placed around the point center. dims specifies the width and height of the magnification
        map in units of arc. resolution specifies the dimensions of the magnification map.
        The signals allow for feedback on progress of the calculation. If none are supplied, output is silenced, 
        causing the calulation to go slightly faster. If a NullSignal is supplied, progress updates are sent 
        to the standard output.
        '''
        resx = resolution.x
        resy = resolution.y
        stepX = dims.to('rad').x/resx   
        stepY = dims.to('rad').y/resy
        start = center - dims/2
        x0 = start.to('rad').x
        y0 = start.to('rad').y+dims.to('rad').y
        radius = self.parameters.queryQuasarRadius
        def generator(i,j,k):
            if k == 0:
                return x0 + i*stepX
            elif k == 1:
                return y0 - j*stepY        
        query_points = np.fromfunction(generator)
        return self._rdd_grid.query_points(query_points,radius,sc)

