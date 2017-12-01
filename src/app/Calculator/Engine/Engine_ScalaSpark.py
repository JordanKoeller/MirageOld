from __future__ import division

from pyspark import SparkContext, SparkConf
import numpy as np
import math as CMATH
from .Engine import Engine
from astropy import constants as const

if __name__ == '__main__':
    conf = SparkConf().setAppName("Lensing Simulation")
    sc = SparkContext(conf=conf)
    sc.setLogLevel('WARN')

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
 # 20   def createRDDGrid(
 # 21     stars: RDD[(Double, Double, Double)],
 # 22     pointConstant: Double,
 # 23     sisConstant: Double,
 # 24     shearMag: Double,
 # 25     shearAngle: Double,
 # 26     dTheta: Double,
 # 27     centerX: Double,
 # 28     centerY: Double,
 # 29     width: Double,
 # 30     height: Double): Unit = {

        dS = self.parameters.quasar.angDiamDist.to('lyr').value
        dL = self.parameters.galaxy.angDiamDist.to('lyr').value
        dLS = self.parameters.dLS.to('lyr').value
        stars = self.parameters.stars
        starsLst = map(lambda lst:(lst[0],lst[1],lst[2]),stars)
        args = (sc.parallelize(starsLst)._jrdd,
                4*(const.G/const.c/const.c).to('lyr/solMass').value*dLS/dS/dL,
                4*CMATH.pi*self.parameters.galaxy.velocityDispersion*2*(const.c**-2).to('s2/km2').value*dLS/dS,
                self.parameters.galaxy.shear.magnitude,
                self.parameters.galaxy.shear.angle.to('rad').value,
                self.parameters.dTheta.to('rad').value,
                self.parameters.galaxy.position.to('rad').x,
                self.parameters.galaxy.position.to('rad').y,
                _width,
                _height
                )
        sc._jvm.main.Main.createRDDGrid(*args)
        print("FINSIHED RAY TRACING AND MAPPING")
        
        '''
        Calulates and returns a 2D magnification map of the magnification coefficients 
        of a quasar placed around the point center. dims specifies the width and height of the magnification
        map in units of arc. resolution specifies the dimensions of the magnification map.
        The signals allow for feedback on progress of the calculation. If none are supplied, output is silenced, 
        causing the calulation to go slightly faster. If a NullSignal is supplied, progress updates are sent 
        to the standard output.
        '''
    def makeMagMap(self, center, dims, resolution,*args,**kwargs):
        """[summary]
        
        [description]
        
        Arguments:
            center {Vector2D} -- Center coordinates of the magnification map, in units of arc.
            dims {Vector2D} -- Width and height in units of arc for the canvas.
            resolution {Vector2D} -- Number of pixels for the maginfication map, in the x and y directions.
            *args {} -- To prevent optional signals passed in from raising an exception.
            **kwargs {} -- To prevent optional signals passed in from raising an exception.
        
        Returns:
            np.ndarray[shape=resolution, dtype=int] -- An array of the ratio of the magnification of the image, with and without microlensing.
        """
        resx = resolution.x
        resy = resolution.y
        stepX = dims.to('rad').x/resx   
        stepY = dims.to('rad').y/resy
        start = center - dims/2
        x0 = start.to('rad').x
        y0 = start.to('rad').y+dims.to('rad').y
        radius = self.parameters.queryQuasarRadius
        pts = []
        for i in range(0,resx):
            for j in range(0,resy):
                pts.append(((i,j),(x0+i*stepX,y0-j*stepY)))
        ptsJRDD = sc.parallelize(pts,1)._jrdd
        retRDD = sc._jvm.main.Main.queryPoints(ptsJRDD,radius)
        ret = np.ndarray((res,resy))
        retLst = retRDD.collect()
        for elem in retLst:
            ret[elem[0],elem[1]] = elem[2]
        return ret







 # 55   def queryPoints(pts: RDD[((Int, Int), (Double, Double))], radius: Double):RDD[(Int,Int,Double)] = {
