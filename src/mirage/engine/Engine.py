'''
Created on Jan 7, 2018

@author: jkoeller
'''
import math
from astropy import constants as const
import numpy as np

from astropy import units as u
from mirage.utility import Vector2D

from .CalculationDelegate import CalculationDelegate
import copy

from math import sin, cos, sqrt, atanh, atan

class Engine(object):
    '''
    classdocs
    '''


    def __init__(self,calculation_delegate):
        '''
        Constructor
        '''
        self.bind_calculation_delegate(calculation_delegate)
        self._parameters = None
        self._preCalculating = False
        self._center = None

    @property
    def core_count(self):
        return self._calcDel.core_count
    
        
    @property
    def parameters(self):
        return self._parameters

    @property
    def calculation_delegate(self):
        return self._calcDel
    
    def bind_calculation_delegate(self,delegate):
        assert isinstance(delegate,CalculationDelegate), "Must use a CalculationDelegate instance to bind to engine."
        self._calcDel = delegate
#         self._calcDel.bind_manager(self)
    
    def reconfigure(self):
        import random
        self._center = None
        self._center = self.get_center_coords()
        if len(self.parameters.stars) > 0 and self.parameters.raw_magnification is None:
            rawMag = self.calculate_raw_magnification()
            print("Found " + str(rawMag) + " points")
            self.parameters.setRawMag(int(rawMag))
            return self._calcDel.reconfigure(self.parameters)
        else:
            if self.parameters.raw_magnification is None:
                print("CRAP had to do it again")
                self._calcDel.reconfigure(self.parameters)
                x = self._center.x 
                y = self._center.y
                r = self.parameters.queryQuasarRadius
                rawMag = self._calcDel.query_data_length(x,y,r)
                self.parameters.setRawMag(rawMag)
                return self._calcDel.reconfigure(self.parameters)
            else:
                return self._calcDel.reconfigure(self.parameters)


    def calculate_raw_magnification(self):
        self._center = None
        self._center = self.get_center_coords()
        print("calculating raw mag")
        x = self._center.x
        y = self._center.y
        backup = copy.deepcopy(self.parameters)
        cp = copy.deepcopy(self.parameters)
        cp.clear_stars()
        # self._calcDel.reconfigure(cp)  
        rawMag = self._calcDel.query_single_point(cp,x,y,cp.queryQuasarRadius)
        print("Raw Mag of " + str(rawMag))
        print("Queried rad of " + str(cp.queryQuasarRadius))
        return rawMag


    def query_line(self,pts,r=None):
        arr = np.array([pts.to('rad').value.tolist()])
        values = self._calcDel.sample_light_curves(arr,r.to('rad').value)[0]
        return self.normalize_magnification(values,r)




    
    def make_light_curve(self,mmin,mmax,resolution):
        ret = self._calcDel.make_light_curve(mmin,mmax,resolution)
        return self.normalize_magnification(ret)
    
    def sample_light_curves(self,lines):
        '''
        Function for randomly sampling many light curves out of a starfield at once.
        
        Works as follows: 
        
        Accepts a list of astropy Quantitys specifying the coordinates to query for each line.
        '''
        # bounding_box.center = self.get_center_coords()
        # for row in lines.value:
        #     slc= __slice_line(row,bounding_box,resolution)
        #     slices.append(np.array(slc).T)
        if isinstance(lines[0],u.Quantity):
            for i in range(len(lines)): lines[i] = lines[i].to('rad').value
        lightCurves = self._calcDel.sample_light_curves(lines,self.parameters.queryQuasarRadius)
        ret = []
        for curveInd in range(len(lightCurves)):
            c = self.normalize_magnification(lightCurves[curveInd])
            qPts = lines[curveInd]
            begin = qPts[0]
            end = qPts[-1]
            ret.append([c,np.array([begin,end])])
        return ret
        #slices is a list of numpy arrays.
        #Each numpy array is of shape (N,2)
        #So arr[:,0]  gives xvals, arr[:,1] gives yvals
        
        #Now I need to add a column for the number of points to query. Then I can pass along 
        #        to the calculation delegate.
        
        
        
        
        
    
    def make_mag_map(self,center,dims,resolution,radius=None):
        center = self.get_center_coords(self.parameters)
        ret = self._calcDel.make_mag_map(center,dims,resolution)
        print(ret)
        # return ret
        return self.normalize_magnification(ret,radius)

    def get_frame(self,x=None,y=None,r=None):
        return self._calcDel.get_frame(x,y,r)
    
        
    def ray_trace(self):
        return self._calcDel.ray_trace(self.parameters)
    
    def get_center_coords(self, params=None):
        '''Calculates and returns the location of a ray sent out from the center of the screen after 
        projecting onto the Source Plane.'''
        # Pulling parameters out of parameters class
        if not self._center:
            parameters = params or self.parameters
            dS = parameters.quasar.angDiamDist.value
            dLS = parameters.dLS.value
            shearMag = parameters.galaxy.shear.magnitude
            shearAngle = parameters.galaxy.shear.angle.value
            centerX = parameters.galaxy.position.to('rad').x
            centerY = parameters.galaxy.position.to('rad').y
            sis_constant = np.float64(4 *  math.pi * parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
            pi2 = math.pi / 2
            # Calculation variables
            resx = 0
            resy = 0
            # Calculation is Below
            incident_angle_x = 0.0
            incident_angle_y = 0.0
            q = parameters.ellipticity
            tq = parameters.ellipAng
            q1 = sqrt(1-q*q)
            try:
                # SIS
                deltaR_x = incident_angle_x - centerX
                deltaR_y = incident_angle_y - centerY
                r = math.sqrt(deltaR_x * deltaR_x + deltaR_y * deltaR_y)
                if r == 0.0:
                    resx += deltaR_x 
                    resy += deltaR_y
                else:
                    if parameters.ellipticity == 1.0:
                        resx += deltaR_x * sis_constant / r 
                        resy += deltaR_y * sis_constant / r 
                    else:
                        eex = (deltaR_x*sin(tq)+deltaR_y*cos(tq))
                        eey = (deltaR_y*sin(tq)-deltaR_x*cos(tq))
                        ex =  sis_constant/q1*atan(q1*eex/sqrt(q*q*eex*eex+eey*eey))
                        ey = sis_constant/q1*atanh(q1*eey/sqrt(q*q*eex*eex+eey*eey))
                        resx += ex*sin(tq) - ey*cos(tq)
                        resy += ex*cos(tq) + ey*sin(tq)
                
                # Shear
                phi = 2 * (pi2 - shearAngle) - math.atan2(deltaR_y, deltaR_x)
                resx += shearMag * r * math.cos(phi)
                resy += shearMag * r * math.sin(phi)
                resx = deltaR_x - resx
                resy = deltaR_y - resy
            except ZeroDivisionError:
                resx = 0.0
                resy = 0.0
            self._center =  Vector2D(resx, resy, 'rad')
        return self._center

    def save_rays(self,fname):
        self._calcDel.save_rays(fname)
    
    
    @property
    def true_luminosity(self):
        '''Returns the apparent radius of the quasar in units of pixels^2'''
        return math.pi * (self.parameters.quasar.radius.value / self.parameters.dTheta.value) ** 2


    
    def update_parameters(self, parameters):
        """Provides an interface for updating the parameters describing the lensed system to be modeled.

        If the new system warrants a recalculation of spatial data, will call the function 'reconfigure' automatically"""

        if self._parameters is None:
            self._parameters = parameters
            if self._parameters.galaxy.percentStars > 0 and self._parameters.galaxy.stars == []:
                self._parameters.regenerateStars()
            self.reconfigure()
        elif not self._parameters.isSimilar(parameters):
            self._parameters.update(canvasDim=parameters.canvasDim)
            if self._parameters.isSimilar(parameters):
                self._parameters = parameters
                if self._parameters.galaxy.percentStars > 0 and self._parameters.galaxy.stars == []:
                    self._parameters.regenerateStars()
            else:
                self._parameters = parameters
            self.reconfigure()
        else:
            parameters.setStars(self._parameters.stars)
            self._parameters = parameters
            
    def normalize_magnification(self,values,radius = None):
        assert isinstance(values, np.ndarray) or isinstance(values,float) or isinstance(values,int), "values must be a numeric type or numpy array."
        # self._rawMag = 100
        if radius:
            conversion_factor = self.parameters.approximate_raw_magnification(radius)
            print("Conversion factor = " + str(conversion_factor))
            return values / conversion_factor
        elif self.parameters.raw_magnification:
            return values / self.parameters.raw_magnification
        else:
            raise ValueError("Did not contain a raw magnification value")

            


    
