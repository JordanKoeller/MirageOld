'''
Created on Jan 7, 2018

@author: jkoeller
'''
import math
from astropy import constants as const
import numpy as np

from app.utility import Vector2D

from .CalculationDelegate import CalculationDelegate

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
        return self._calcDel.reconfigure(self.parameters)
    
    def make_light_curve(self,mmin,mmax,resolution):
        ret = self._calcDel.make_light_curve(mmin,mmax,resolution)
        return self.normalize_magnification(ret)
    def make_mag_map(self,center,dims,resolution):
        ret = self._calcDel.make_mag_map(center,dims,resolution)
        return self.normalize_magnification(ret)

    def get_frame(self,x=None,y=None,r=None):
        return self._calcDel.get_frame(x,y,r)
    
        
    def ray_trace(self):
        return self._calcDel.ray_trace(self.parameters)
    
    def get_center_coords(self, params=None):
        '''Calculates and returns the location of a ray sent out from the center of the screen after 
        projecting onto the Source Plane.'''
        # Pulling parameters out of parameters class
        parameters = params or self.parameters
        dS = parameters.quasar.angDiamDist.value
        dLS = parameters.dLS.value
        shearMag = parameters.galaxy.shear.magnitude
        shearAngle = parameters.galaxy.shear.angle.value
        centerX = parameters.galaxy.position.to('rad').x
        centerY = parameters.galaxy.position.to('rad').y
        sis_constant =     np.float64(4 * math.pi * parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
        pi2 = math.pi / 2

        # Calculation variables
        resx = 0
        resy = 0

        # Calculation is Below
        incident_angle_x = 0.0
        incident_angle_y = 0.0
        
        try:
            # SIS
            deltaR_x = incident_angle_x - centerX
            deltaR_y = incident_angle_y - centerY
            r = math.sqrt(deltaR_x * deltaR_x + deltaR_y * deltaR_y)
            if r == 0.0:
                resx += deltaR_x 
                resy += deltaR_y
            else:
                resx += deltaR_x * sis_constant / r 
                resy += deltaR_y * sis_constant / r 
            
            # Shear
            phi = 2 * (pi2 - shearAngle) - math.atan2(deltaR_y, deltaR_x)
            resx += shearMag * r * math.cos(phi)
            resy += shearMag * r * math.sin(phi)
            resx = deltaR_x - resx
            resy = deltaR_y - resy
        except ZeroDivisionError:
            resx = 0.0
            resy = 0.0
        return Vector2D(resx, resy, 'rad')
    
    
    @property
    def true_luminosity(self):
        '''Returns the apparent radius of the quasar in units of pixels^2'''
        return math.pi * (self.parameters.quasar.radius.value / self.parameters.dTheta.value) ** 2

    def raw_magnification(self, x, y):
        print("\n\n\n MAY BE BROKEN IN NORMALIZING MAGNIFICATION. NEED TO DOUBLE CHECK LATER \n\n\n")
        import copy
        rawP = copy.deepcopy(self.parameters)
        rawP.galaxy.update(percentStars=0)
        self.update_parameters(rawP)
        rawMag = self._calcDel.query_data_length(x, y, rawP.queryQuasarRadius)
        return rawMag
    
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
            
    def normalize_magnification(self,values):
        assert isinstance(values, np.ndarray) or isinstance(values,float) or isinstance(values,int), "values must be a numeric type or numpy array."
        center = self.get_center_coords()
        rawMag = self.raw_magnification(center.x, center.y)
        return values / rawMag
            
            
