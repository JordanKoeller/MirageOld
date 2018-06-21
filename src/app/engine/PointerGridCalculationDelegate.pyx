# cython: boundscheck=False
# cython: cdivision=True
# cython: wraparound=False

from __future__ import division

from .CalculationDelegate cimport CalculationDelegate
from libcpp cimport bool
from app.utility.PointerGrid cimport PointerGrid
from libcpp.pair cimport pair
from libcpp.vector cimport vector
import numpy as np 
cimport numpy as np

from libc cimport math as CMATH

from app.preferences import GlobalPreferences
from app.utility import zeroVector, Vector2D

import ctypes
import os
import random
import time
import math

from astropy import constants as const
from astropy import units as u
from astropy.cosmology import WMAP7 as cosmo
import cython
from cython.parallel import prange

from libc.math cimport sin, cos, atan2, sqrt

cdef class PointerGridCalculationDelegate(CalculationDelegate):

    def __init__(self):
        CalculationDelegate.__init__(self)
        self._parameters = None
        self.__preCalculating = False
        self.core_count = GlobalPreferences['core_count']

    cpdef void reconfigure(self, object parameters):
        self._parameters = parameters
        self.__grid = PointerGrid()
        begin = time.clock()
        self.__preCalculating = True
        finalData = self.ray_trace()
        self.build_data(finalData[0], finalData[1], int(4 * finalData[0].shape[0] ** 2))
        del(finalData)
        self.__preCalculating = False
        print("Time calculating = " + str(time.clock() - begin) + " seconds.")
            
    cpdef object make_light_curve(self, object mmin, object mmax, int resolution):
        while self.__preCalculating:
            time.sleep(0.1)
        mmax = mmax.to('rad')
        mmin = mmin.to('rad')
        cdef double stepX = (mmax.x - mmin.x) / resolution
        cdef double stepY = (mmax.y - mmin.y) / resolution
        cdef np.ndarray[np.float64_t, ndim = 1] yAxis = np.ones(resolution)
        cdef int i = 0
        cdef double radius = self._parameters.queryQuasarRadius
        cdef double x = mmin.x
        cdef double y = mmin.y
        cdef bool hasVel = False  # Will change later
        cdef double trueLuminosity = self.trueLuminosity
        cdef int aptLuminosity = 0
        with nogil:
            for i in range(0, resolution):
                x += stepX
                y += stepY
                aptLuminosity = self.__grid.find_within_count(x, y, radius)  # Incorrect interface
                yAxis[i] = (< double > aptLuminosity)
        return yAxis  
    
    cpdef object make_mag_map(self, object center, object dims, object resolution):
        cdef int resx = < int > resolution.x
        cdef int resy = < int > resolution.y
        cdef np.ndarray[np.float64_t, ndim = 2] retArr = np.ndarray((resx, resy), dtype=np.float64)
        cdef double stepX = dims.to('rad').x / resolution.x
        cdef double stepY = dims.to('rad').y / resolution.y
        cdef int i = 0
        cdef int j = 0
        cdef double x = 0
        cdef double y = 0
        start = center - dims / 2
        cdef double x0 = start.to('rad').x
        cdef double y0 = start.to('rad').y + dims.to('rad').y
        cdef double radius = self._parameters.queryQuasarRadius
        cdef double roverX, roverY
        for i in prange(0, resx, nogil=True, schedule='guided', num_threads=self.core_count):
            for j in range(0, resy):
                roverX = x0 + i * stepX
                roverY = y0 - stepY * j
                retArr[i, j] = (< double > self.__grid.find_within_count(roverX, roverY, radius))
        return retArr
    
    cpdef object sample_light_curves(self, object pts, double radius): #OPtimizations are definitely possible by cythonizing more, especially the last for loop.
        cdef int i = 0
        cdef int j = 0
        cdef int counts = 0
        cdef double x, y
        lengths = []
        for i in range(len(pts)):
            lengths.append(pts[i].shape[0])
        cdef int max_length = 0
        max_length = max(lengths)
        cdef np.ndarray[np.float64_t,ndim=3] queries = np.zeros((len(pts),max_length,2),dtype=np.float64) #added
        cdef np.ndarray[np.int32_t,ndim=2] ret_pts = np.zeros((len(pts),max_length),dtype=np.int32) #added
        queries = queries - 1.0
        for i in range(0,len(pts)):
            for j in range(0,len(pts[i])):
                queries[i,j] = pts[i][j]
        cdef np.ndarray[np.int32_t, ndim = 1] curve_lengths = < np.ndarray[np.int32_t, ndim = 1] > np.array(lengths,dtype=np.int32)
        cdef int end = len(pts)
        # Now need to actually query them
        for i in prange(0, end, nogil=True, schedule='guided', num_threads=self.core_count):
            for j in range(0, curve_lengths[i]):
                x = queries[i,j,0]
                y = queries[i,j,1]
                counts = self.__grid.find_within_count(x, y, radius)
                ret_pts[i,j] = counts
        retLines = []
        # queryEnds = []
        for i in range(0, len(pts)):
            lineCounts = np.ndarray(curve_lengths[i],dtype=np.int32)
            # queriedPts = pts[i]
            # startLine = queriedPts[0]
            # last = queriedPts.shape[0]
            # endLine = queriedPts[last-1]
            # q = np.array([list(startLine),list(endLine)])
            # queryEnds.append(q)
            for j in range(0,curve_lengths[i]):
                lineCounts[j] = ret_pts[i,j]
            retLines.append(lineCounts)
        return retLines
    

    cpdef object get_frame(self, object x, object y, object r):
        """
        Returns a 2D numpy array, containing the coordinates of pixels illuminated by the source specified in the system's parameters.
        """
        # Possible optimization by using vector data rather than copy?
        while self.__preCalculating:
            print("waiting")
            time.sleep(0.1)
        begin = time.clock()
        cdef double qx = 0
        cdef double qy = 0
        cdef double qr = 0
        qx = x or self._parameters.queryQuasarX
        qy = y or self._parameters.queryQuasarY
        qr = r or self._parameters.queryQuasarRadius
        cdef vector[pair[int, int]] ret = self.query_data(qx, qy, qr)
        cdef int retf = ret.size()
        cdef int i = 0
        cdef np.ndarray[np.int32_t, ndim = 2] fret = np.ndarray((ret.size(), 2), dtype=np.int32)
        with nogil:
            for i in range(0, retf):
                fret[i, 0] = < int > ret[i].first
                fret[i, 1] = < int > ret[i].second
#         print(1/(time.clock()-begin))
        return fret
    
    cpdef unsigned int query_data_length(self, object x, object y, object radius):
        cdef double xx = x or self._parameters.queryQuasarX
        cdef double yy = y or self._parameters.queryQuasarY
        cdef double r = radius or self._parameters.queryQuasarRadius
        with nogil:
            return self.__grid.find_within_count(xx, yy, r)

    cdef vector[pair[int, int]] query_data(self, double x, double y, double radius) nogil:
        """Returns all rays that intersect the source plane within a specified radius of a location on the source plane."""
        cdef vector[pair[int, int]] ret = self.__grid.find_within(x, y, radius)
        return ret
        

    cdef build_data(self, np.ndarray[np.float64_t, ndim=2] xArray, np.ndarray[np.float64_t, ndim=2] yArray, int binsize):
        """Builds the spatial data structure, based on the passed in numpy arrays representing the x and y values of each
            pixel where it intersects the source plane after lensing effects have been accounted for."""
        cdef int w = xArray.shape[0]
        cdef int h = xArray.shape[1]
        cdef int nd = 2
        cdef double * x = < double *> xArray.data 
        cdef double * y = < double *> yArray.data
        with nogil:
            self.__grid = PointerGrid(x, y, h, w, nd, binsize)
    

    cdef ray_trace(self):
        '''Ray-traces the system on the CPU. Does not require openCL
        
        Must call reconfigure() before this method.
        '''
        begin = time.clock()
        cdef int height = self._parameters.canvasDim
        cdef int width = self._parameters.canvasDim
        height = height // 2
        width = width // 2
        cdef double dTheta = self._parameters.dTheta.value
        cdef np.ndarray[np.float64_t, ndim = 2] result_nparray_x = np.zeros((width * 2, height * 2), dtype=np.float64)
        cdef np.ndarray[np.float64_t, ndim = 2] result_nparray_y = np.zeros((width * 2, height * 2), dtype=np.float64)
        cdef double dS = self._parameters.quasar.angDiamDist.to('lyr').value
        cdef double dL = self._parameters.galaxy.angDiamDist.to('lyr').value
        cdef double dLS = self._parameters.dLS.to('lyr').value
        cdef np.ndarray[np.float64_t, ndim = 1] stars_mass, stars_x, stars_y
        cdef int numStars = 0
        if self._parameters.galaxy.percentStars > 0.0:
            stars_mass, stars_x, stars_y = self._parameters.galaxy.starArray
            numStars = len(stars_x)
        cdef double shearMag = self._parameters.galaxy.shear.magnitude
        cdef double shearAngle = self._parameters.galaxy.shear.angle.value
        cdef double centerX = self._parameters.galaxy.position.to('rad').x
        cdef double centerY = self._parameters.galaxy.position.to('rad').y
        cdef double sis_constant = np.float64(4 * math.pi * self._parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
        cdef double point_constant = (4 * const.G / const.c / const.c).to("lyr/solMass").value * dLS / dS / dL
        cdef double pi2 = math.pi / 2
        cdef int x, y, i
        cdef double incident_angle_x, incident_angle_y, r, deltaR_x, deltaR_y, phi
        for x in prange(0, width * 2, 1, nogil=True, schedule='static', num_threads=self.core_count):
            for y in range(0, height * 2):
                incident_angle_x = (x - width) * dTheta
                incident_angle_y = (height - y) * dTheta

                for i in range(numStars):
                    deltaR_x = incident_angle_x - stars_x[i]
                    deltaR_y = incident_angle_y - stars_y[i]
                    r = deltaR_x * deltaR_x + deltaR_y * deltaR_y
                    if r != 0.0:
                        result_nparray_x[x, y] += deltaR_x * stars_mass[i] * point_constant / r;
                        result_nparray_y[x, y] += deltaR_y * stars_mass[i] * point_constant / r;                
#                 
                # SIS
                deltaR_x = incident_angle_x - centerX
                deltaR_y = incident_angle_y - centerY
                r = sqrt(deltaR_x * deltaR_x + deltaR_y * deltaR_y)
                if r != 0.0:
                    result_nparray_x[x, y] += deltaR_x * sis_constant / r 
                    result_nparray_y[x, y] += deltaR_y * sis_constant / r

                # Shear
                phi = 2 * (pi2 - shearAngle) - CMATH.atan2(deltaR_y, deltaR_x)
                result_nparray_x[x, y] += shearMag * r * CMATH.cos(phi)
                result_nparray_y[x, y] += shearMag * r * CMATH.sin(phi)
                result_nparray_x[x, y] = deltaR_x - result_nparray_x[x, y]
                result_nparray_y[x, y] = deltaR_y - result_nparray_y[x, y]
                
        return (result_nparray_x, result_nparray_y)
    
