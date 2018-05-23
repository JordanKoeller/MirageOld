'''
Created on Jan 7, 2018

@author: jkoeller
'''
import math
from astropy import constants as const
import numpy as np

from astropy import units as u
from app.utility import Vector2D

from .CalculationDelegate import CalculationDelegate
import copy

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
        self._rawMag = None
        self._center = None
        
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
        self._center = None
        self._rawMag = None
        backup = copy.deepcopy(self.parameters)
        cp = copy.deepcopy(self.parameters)
        cp.galaxy.update(percentStars=0)
        self._calcDel.reconfigure(cp)
        self._center = self.get_center_coords()
        x = self._center.x 
        y = self._center.y
        self._rawMag = self._calcDel.query_data_length(x,y,cp.queryQuasarRadius)
        return self._calcDel.reconfigure(self.parameters)


    
    def make_light_curve(self,mmin,mmax,resolution):
        ret = self._calcDel.make_light_curve(mmin,mmax,resolution)
        return self.normalize_magnification(ret)
    
    def sample_light_curves(self,lines,bounding_box,resolution = u.Quantity(0.5,'uas')):
        '''
        Function for randomly sampling many light curves out of a starfield at once.
        
        Works as follows:
        
        To make a line, need two points. Thus, we start with a numpy array of (number,4) dimension.
        It has number many rows, to specify number many coordinates.
        In each row are four doubles, representing [xStart, yStart, xEnd, yEnd]
        
        This is then wrapped in a astropy units.Quantity, to allow for easy rescaling.
        '''
        bounding_box.center = self.get_center_coords()
        
        print("Sampling many curves")
        def __slice_line(pts,bounding_box,resolution):
            #pts is an array of [x1,y1,x2,y2]
            #Bounding box is a MagMapParameters instance
            #resolution is a specification of angular separation per data point
            x1,y1,x2,y2 = pts
            m = (y2 - y1)/(x2 - x1)
            angle = math.atan(m)
            resolution = resolution.to('rad')
            dx = resolution.value*math.cos(angle)
            dy = resolution.value*math.sin(angle)
            dims = bounding_box.dimensions.to('rad')
            center = bounding_box.center.to('rad')
            lefX = center.x - dims.x/2
            rigX = center.x + dims.x/2
            topY = center.y + dims.y/2 
            botY = center.y - dims.y/2
            flag = True
            x = x1
            y = y1
            retx = [] 
            rety = [] 
            while flag:
                x -= dx
                y -= dy
                flag = x >= lefX and x <= rigX and y >= botY and y <= topY
            flag = True
            while flag:
                x += dx
                y += dy
                retx.append(x)
                rety.append(y)
                flag = x >= lefX and x <= rigX and y >= botY and y <= topY
            retx = retx[:-1]
            rety = rety[:-1]
            return [retx,rety]
        
        slices = []
        for row in lines.value:
            slice= __slice_line(row,bounding_box,resolution)
            slices.append(np.array(slice).T)
        lightCurves = self._calcDel.sample_light_curves(slices,self.parameters.queryQuasarRadius)
        ret = []
        print(lightCurves[0][0].shape)
        print(lightCurves[0][1].shape)
        for curve in lightCurves:
            #c = self.normalize_magnification(curve[0])
            c = curve[0]
            ret.append([c,curve[1]])
        return ret
        print(ret[0][0].shape)
        print(ret[0][1].shape)
        #slices is a list of numpy arrays.
        #Each numpy array is of shape (N,2)
        #So arr[:,0]  gives xvals, arr[:,1] gives yvals
        
        #Now I need to add a column for the number of points to query. Then I can pass along 
        #        to the calculation delegate.
        
        
        
        
        
    
    def make_mag_map(self,center,dims,resolution):
        center = self.get_center_coords(self.parameters)
        ret = self._calcDel.make_mag_map(center,dims,resolution)
        return ret
        #return self.normalize_magnification(ret)

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
            self._center =  Vector2D(resx, resy, 'rad')
        return self._center
    
    
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
            
    def normalize_magnification(self,values):
        assert isinstance(values, np.ndarray) or isinstance(values,float) or isinstance(values,int), "values must be a numeric type or numpy array."
        if self._rawMag:
            return values / rawMag
        else:
            raise ValueError("Did not contain a raw magnification value")
            


    
