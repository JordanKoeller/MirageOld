'''
Created on Jun 8, 2017

@author: jkoeller
'''

from builtins import property
import math

from astropy import units as u


class Vector2D(object):
    '''
    Uses astropy units for better stuffs
    '''


    def __init__(self, x,y,unit=None):
        '''
        Constructor
        '''
        self.__values = u.Quantity([x,y],unit)

    @property
    def x(self):
        return self.__values[0].value
    
    @property
    def y(self):
        return self.__values[1].value
    
    @property
    def _vals(self):
        return self.__values[:]
    

    
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

    def __str__(self):
        "Pretty print"
        if self.unit != None:
            return "("+str(self.__round_to_n(self.x))+","+str(self.__round_to_n(self.y))+" " +str(self.unit) + ")"
        else:
            return "("+str(self.__round_to_n(self.x))+","+str(self.__round_to_n(self.y))+")"



zeroVector = Vector2D(0.0,0.0,None)
        
        
        