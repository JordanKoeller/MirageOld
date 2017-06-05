'''
Created on Jun 2, 2017

@author: jkoeller
'''
from Models import Drawable
from Utility import Vector2D
from Utility import zeroVector


class Movable(Drawable):
    '''
    classdocs
    '''

    __observedPosition = zeroVector
    __velocity = zeroVector
    
    def __init__(self, position,velocity):
        '''
        Constructor
        '''
        super(Movable, self).__init__()
        self.__velocity = velocity
        self.__observedPosition = position
        
    @property
    def velocity(self):
        return self.__velocity.to('rad')

    def updateMovable(self,position,velocity):
        if velocity != None:
            self.__velocity = velocity
        self.__observedPosition = self.position
        
    @property
    def position(self):
        return self.__observedPosition.to('rad')
    @property
    def observedPosition(self):
        return self.__observedPosition.to('rad')

    def setTime(self, t):
        self.__observedPosition = self._Drawable__position + (self.velocity * t)

    def incrementTime(self,dt):
        self.__observedPosition = self.__observedPosition + self.velocity * dt

    def setPos(self,x,y = None):
        if y == None:
            self.__observedPosition = x
        else:
            self.__observedPosition = Vector2D(x,y)
    
    def circularPath(self):
        vel = self.velocity.magnitude()
        x,y = self.observedPosition.asTuple
        tangent = 0
        try:
            tangent = -x/y
        except ZeroDivisionError as e:
            tangent = -0
        self.__velocity = Vector2D(1,tangent).normalized()*self.velocity.magnitude()