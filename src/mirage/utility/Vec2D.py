'''
Created on Jun 8, 2017

@author: jkoeller
'''

import math
from math import sin, cos, sqrt

from astropy import units as u
from .JSON import JSONable


class Vector2D(JSONable):
    '''
    Uses astropy units for better stuffs
    '''


    def __init__(self, x,y,unit=None) -> None:
        '''
        Constructor
        '''
        self.__values = u.Quantity([x,y],unit)

    @property
    def json(self):
        ret = {}
        ret['x'] = self.x
        ret['y'] = self.y
        if self.unit != None or self.unit.to_string() != "":
            ret['unit'] = self.unit.to_string()
        return ret

    @classmethod
    def from_json(cls,js):
        if 'unit' in js:
            return cls(js['x'],js['y'],js['unit'])
        else:
            return cls(js['x'],js['y'])

    @property
    def x(self):
        return self.__values[0].value
    
    @property
    def y(self):
        return self.__values[1].value
    
    @property
    def _vals(self):
        return self.__values[:]
    

    def copy(self):
        return Vector2D(self.x,self.y,self.unit)
        
    @property
    def unit(self):
        return self.__values.unit
        
        
    def distanceTo(self, other,unit = None):
        "Calculates linear distance between two points"
        if unit != None:
            self.to(unit)
            other.to(unit)
        diff = (other - self)
        return u.Quantity(math.sqrt(diff.x**2+diff.y**2),self.unit)
    
    def magnitude(self):
        return math.sqrt(self.x**2+self.y**2)

    def magWithUnits(self):
        return u.Quantity(self.magnitude(),self.unit)
    
    def normalized(self):
        mag = self.magnitude()
        return self/mag
    
    def setUnit(self,unit=None):
        self.__values = u.Quantity([self.x,self.y],unit)
        return self
    
    @property
    def orthogonal(self):
        return Vector2D(self.y,self.x,self.unit)
    
    def __eq__(self,other):
        if other == None:
            return False
        return self.x == other.x and self.y == other.y and self.unit == other.unit

    def __neq__(self,other):
        return not self.__eq__(other)
        
    def __add__(self, that):
        "Returns a new vector that is the sum of self and the passed in vector."
        vals = self._vals + that._vals
        return Vector2D(vals[0].value,vals[1].value,vals.unit)

    def __sub__(self, that):
        "Returns a new vector after subtracting the argument from self."
        vals = self._vals - that._vals
        return Vector2D(vals[0].value,vals[1].value,vals.unit)
    
    def __mul__(self, that):
        "Returns the dot product of two vectors."
        if isinstance(that,float) or isinstance(that, int):
            return Vector2D(self.x*that,self.y*that,self.unit)
        elif isinstance(that,u.Quantity):
            vals = self._vals*that
            return Vector2D(vals[0].value,vals[1].value,vals.unit)
        else:
            vals = self._vals * that._vals
            return Vector2D(vals[0].value,vals[1].value,vals.unit)
        
    def __truediv__(self, that):
        "Returns the dot product of two vectors."
        if isinstance(that,Vector2D):
            tmp = self._vals/that._vals
            return Vector2D(tmp[0],tmp[1],tmp.unit)
        else:
            return Vector2D(self.x/that,self.y/that,self.unit)
        
    def __neg__(self):
        "Returns a new vector in the opposite direction of self."
        return self * -1
    def neg(self):
        return self * -1
        
    @property
    def asTuple(self):
        return (self.x,self.y)
    
    @property
    def angle(self):
        return math.atan2(self.y,self.x)


    def unitless(self):
        return Vector2D(self.x,self.y,None)
    
    def __round_to_n(self, x,n = 6):
        if x == 0.0:
            return 0
        else:
            return round(float(x), -int(math.floor(math.log10(abs(float(x))))) + (n - 1))
        
    def to(self,unit):
        tmp = self.__values[:]
        tmp = tmp.to(unit)
        return Vector2D(tmp[0].value,tmp[1].value,tmp[0].unit)

    @property
    def asString(self):
        return "("+str(self.x)+","+str(self.y)+")"


    @classmethod
    def fromTuple(self,args):
        x = args[0]
        y = args[1]
        return Vector2D(x,y)

    def __repr__(self):
        "Pretty print"
        if self.unit != None:
            return "("+str(self.__round_to_n(self.x))+","+str(self.__round_to_n(self.y))+" " +str(self.unit) + ")"
        else:
            return "("+str(self.__round_to_n(self.x))+","+str(self.__round_to_n(self.y))+")"


zeroVector = Vector2D(0.0,0.0,None)


class PolarVector(JSONable):
    """A class for representing polar vectors.
    
    This class is a stripped-down version of the :class:`Vector2D`, designed to be used
    in a polar coordinate frame. Uses the convention of (r,\\theta).
    
    Extends:
        JSONable
    """

    def __init__(self,r:u.Quantity, theta:u.Quantity) -> None:
        self._r = r
        self._theta = theta


    @property
    def magnitude(self):
        return self._r

    @property
    def direction(self):
        return self._theta

    @property
    def primary_axis(self):
        tmp = PolarVector(u.Quantity(1,self.r.unit),self._theta)
        return tmp.to_cartesian()

    @property
    def unit(self):
        return self._r.unit
        
    
    @property
    def r(self):
        return self._r
    
    @property
    def angle(self):
        return self._theta
    
    @property
    def theta(self):
        return self._theta
    

    @classmethod
    def from_cartesian(cls,vector):
        mag = vector.magnitude()*vector.unit
        direction = vector.angle*u.rad
        return cls(mag,direction)

    def to_cartesian(self):
        x = self.r*cos(self.theta.to('rad').value)
        y = self.r*sin(self.theta.to('rad').value)
        return Vector2D(x.value,y.value,x.unit)

    @property 
    def json(self):
        ret = {}
        ret['r'] = self.r.value
        ret['theta'] = self.theta.to('degree').value
        ret['theta_unit'] = 'degree'
        ret['unit'] = self.r.unit.to_string()
        return ret

    @classmethod
    def from_json(cls,js):
        r = js['r']
        t = js['theta']
        tu = js['theta_unit']
        ru = js['unit']
        rr = u.Quantity(r,ru)
        tt = u.Quantity(t,tu)
        return cls(rr,tt)


    def __repr__(self):
        s = "(" + str(self.r.value) + "," + str(self._theta.to('degree').value) + "," + str(self.unit.to_string()) + ")"
        return "(r,theta,unit) = " + s