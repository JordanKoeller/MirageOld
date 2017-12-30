import math

from astropy import constants as const
from astropy import units as u
from pyqtgraph import QtCore, QtGui
from scipy.cluster.vq import vq, kmeans, whiten

import numpy as np
import pyqtgraph as pg 

from app.utility import Vector2D
from app.utility.NullSignal import NullSignal


cimport numpy as np
from .Drawer cimport ImageDrawer
from .ShapeDrawer cimport drawCircle, drawLine

from app.preferences import ColorMap, GlobalPreferences

cdef class LensedImageDrawer(ImageDrawer):

    def __init__(self,signal=NullSignal):
        ImageDrawer.__init__(self,signal)

    
    cpdef draw(self,object args):
        cdef object model = args[0]
        cdef np.ndarray[np.int32_t, ndim=2] pixels = args[1]
        cdef np.ndarray[np.uint8_t, ndim=3] canvas = np.zeros((model.parameters.canvasDim,model.parameters.canvasDim,3), dtype=np.uint8)
        cdef np.ndarray[np.uint8_t, ndim=2] lookup = ColorMap
        if GlobalPreferences['draw_galaxy']:
            model.parameters.galaxy.drawGalaxy(canvas,model)
        if GlobalPreferences['draw_stars'] and model.parameters.galaxy.numStars > 0:
            model.parameters.galaxy.drawStars(canvas,model)
        if GlobalPreferences['draw_quasar']:
            model.parameters.quasar.draw(canvas,model)
        cdef int pixel = 0
        cdef int end = pixels.shape[0]
        cdef np.ndarray[np.uint8_t, ndim=1] colors = self.getColorCode(pixels,model)
        for i in range(0,len(pixels)):
            canvas[pixels[i,0],pixels[i,1]] = lookup[1]
        self.drawBoundary(canvas,model)
#         for i in range(-3,3):
#             for j in range(-3,3):
#                 canvas[500+i,1000+j] = [244,191,66]
        self.signal.emit(canvas)
        return canvas
#         return self.drawImage(canvas,None)

    cdef getColorCode(self, np.ndarray[np.int32_t,ndim=2] pixels, object model):
        cdef x = np.ascontiguousarray(pixels[:,0],dtype=np.float64) 
        cdef y = np.ascontiguousarray(pixels[:,1],dtype=np.float64)
        x = x - model.parameters.canvasDim/2
        y = model.parameters.canvasDim/2 - y
        x = x*model.parameters.dTheta.to('rad').value - model.parameters.galaxy.center.to('rad').x
        y = y*model.parameters.dTheta.to('rad').value - model.parameters.galaxy.center.to('rad').y
        cdef double b = 4 * math.pi * (model.parameters.galaxy.velocityDispersion**2).to('km2/s2')*(const.c** -2).to('s2/km2')*model.parameters.dLS.to('m')/model.parameters.quasar.angDiamDist.to('m')
        cdef double ptConst = (model.parameters.dLS.to('m')/model.parameters.quasar.angDiamDist.to('m')/model.parameters.galaxy.angDiamDist.to('m')*4*const.G*const.c**-2).to('1/solMass').value
        cdef double gamSin = model.parameters.galaxy.shearMag*math.sin(2*(math.pi/2 - model.parameters.galaxy.shearAngle.to('rad').value))
        cdef double gamCos = model.parameters.galaxy.shearMag*math.cos(2*(math.pi/2 - model.parameters.galaxy.shearAngle.to('rad').value))
        cdef x2 =  b*y*y*((x*x+y*y)**(-1.5)) + gamCos
        cdef y2 =  b*x*x*((x*x+y*y)**(-1.5)) - gamCos
        cdef xy = -b*x*y*((x*x+y*y)**(-1.5)) + gamSin
        if model.parameters.galaxy.percentStars:
            starstuff = model.parameters.galaxy.stars
            for i in starstuff:
                dy = (y - i[1] + model.parameters.galaxy.center.to('rad').y)
                dx = (x - i[0] + model.parameters.galaxy.center.to('rad').x)
                x2 -= ptConst*(dy*dy - dx*dx)*i[2]/((dx*dx + dy*dy)**2)
                y2 -= ptConst*(dx*dx - dy*dy)*i[2]/((dx*dx + dy*dy)**2)
                xy += 2*ptConst*(dy * dx)*i[2]/((dx*dx + dy*dy)**2)
        cdef  det = (1-x2)*(1-y2)-(xy)*(xy)
        cdef  trace = (1-x2)+(1-y2)
        cdef ret = np.ndarray((len(x2)),dtype=np.uint8)
        for i in range(0,len(x2)):
            if det[i] > 0.0 and trace[i] > 0.0:
                ret[i] = 1
            else:
                ret[i] = 5
        return ret
        
        
#     cdef void __drawTrackers(self,np.ndarray[np.uint8_t,ndim=3] canvas, object model): #*************NOT OPTIMIZED **************
#         x = ImageFinder.getRoot(-1,-1,model.parameters)
#         xNorm = x
#         xInt = Vector2D(int(xNorm.x),int(xNorm.y))
#         cdef np.ndarray[np.uint8_t, ndim=2] lookup = model.colorMap_arr
#         for i in range(-1,1):
#             for j in range(-1,1):
#                 canvas[i+xInt.x+ int(model.parameters.canvasDim/2)][int(model.parameters.canvasDim/2) - (j+xInt.y)] = lookup[3]

    def drawCriticalRadius(self,canvas,model):
        nu = 2*(model.parameters.galaxy.shearAngle.to('rad').value - model.parameters.quasar.position.angle)
        b = (4*math.pi*(model.parameters.galaxy.velocityDispersion/const.c)**2)*model.parameters.dLS/model.parameters.quasar.angDiamDist
        beta = model.parameters.quasar.position.magnitude()
        r = (b - beta)/(1+model.parameters.galaxy.shearMag*math.cos(nu))
        r /= model.parameters.dTheta.value
        drawCircle(int(model.parameters.canvasDim/2),int(model.parameters.canvasDim/2),r,canvas,3,model)

    def drawCritLines(self,pixels,model,canvas):
        pixels = whiten(pixels)
        imgs = kmeans(pixels,4)
        yInt = model.parameters.canvasDim/2
        yAx = model.parameters.canvasDim/2
        cdef np.ndarray[np.uint8_t, ndim=2] lookup = model.colorMap_arr
        for i in imgs[0]:
            m = -i[0]/i[1]
            drawLine(int(model.parameters.canvasDim),m,0,canvas,3,model)



    cdef void __drawEinsteinRadius(self,np.ndarray[np.uint8_t,ndim=3] canvas,object model): 
        cdef int x0 = model.parameters.galaxy.center.x + model.parameters.canvasDim/2
        cdef int y0 = model.parameters.galaxy.center.y + model.parameters.canvasDim/2
        cdef int radius = model.parameters.einsteinRadius/model.parameters.dTheta.value
        drawCircle(x0,y0,radius, canvas,3,model)


    cdef void drawBoundary(self, np.ndarray[np.uint8_t,ndim=3] canvas,model):
        cdef int x,y,xmax, ymax
        ymax = canvas.shape[1]-1
        cdef np.ndarray[np.uint8_t, ndim=2] lookup = ColorMap
        xmax = canvas.shape[0]-1
        for x in range(0,xmax+1):
            canvas[x,0] = lookup[2]
            canvas[x,1] = lookup[2]
            canvas[x,2] = lookup[2]
            canvas[x,ymax] = lookup[2]
            canvas[x,ymax-1] = lookup[2]
            canvas[x,ymax-2] = lookup[2]
            canvas[0,x] = lookup[2]
            canvas[1,x] = lookup[2]
            canvas[2,x] = lookup[2]
            canvas[xmax,x] = lookup[2]
            canvas[xmax-1,x] = lookup[2]
            canvas[xmax-2,x] = lookup[2]