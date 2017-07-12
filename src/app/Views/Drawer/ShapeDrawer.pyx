import numpy as np 
cimport numpy as np 
from libc cimport math
from libc.math cimport fabs
import cython

@cython.boundscheck(False)  # turn off bounds-checking for entire function
@cython.wraparound(False)
cpdef void drawCircle(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=2] canvas, int color):
	cdef int x = <int> fabs(r)
	cdef int y = 0
	cdef int err = 0
	cdef int canvasDim = canvas.shape[0]
	# 	with nogil:
	while x >= y:
		if x0 + x > 0 and y0 + y > 0 and x0 + x < canvasDim and y0 + y < canvasDim:
				canvas[x0 + x, y0 + y] = color
		if x0 + y > 0 and y0 + x > 0 and x0 + y < canvasDim and y0 + x < canvasDim:
				canvas[x0 + y, y0 + x] = color
		if x0 - y > 0 and y0 + x > 0 and x0 - y < canvasDim and y0 + x < canvasDim:
				canvas[x0 - y, y0 + x] = color 
		if x0 - x > 0 and y0 + y > 0 and x0 - x < canvasDim and y0 + y < canvasDim:
				canvas[x0 - x, y0 + y] = color 
		if x0 - x > 0 and y0 - y > 0 and x0 - x < canvasDim and y0 - y < canvasDim:
				canvas[x0 - x, y0 - y] = color 
		if x0 - y > 0 and y0 - x > 0 and x0 - y < canvasDim and y0 - x < canvasDim:
				canvas[x0 - y, y0 - x] = color 
		if x0 + y > 0 and y0 - x > 0 and x0 + y < canvasDim and y0 - x < canvasDim:
				canvas[x0 + y, y0 - x] = color 
		if x0 + x > 0 and y0 - y > 0 and x0 + x < canvasDim and y0 - y < canvasDim:
				canvas[x0 + x, y0 - y] = color 
		if err <= 0:
			y += 1
			err += 2*y + 1
		if err > 0:
			x -= 1
			err -= 2*x + 1
cpdef void drawLine(int yIntercept, double slope, int yAx, np.ndarray[np.uint8_t, ndim=2] canvas, int color):
	cdef int width = canvas.shape[0]
	cdef int height = canvas.shape[1]
	cdef int x = yAx
	cdef int y = yIntercept
	cdef int i = 0
	with nogil:
		for i in range(0,width):
			y =  (i - yAx)*(<int>slope) + yIntercept 
			if y > -1 and y < height:
				canvas[height - 1 - y,i] = color 
				
				
cpdef void drawSolidCircle(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=2] canvas, int color):
	cdef int rSquared = r * r
	cdef int x, y
	cdef int canvasDim = canvas.shape[0]	
	for x in range(0,r+1):
		for y in range(0,r+1):
			if x*x + y*y <= rSquared:
				if x0+x > 0 and y0+y > 0 and x0+x < canvasDim and y0+y < canvasDim:
					canvas[x0+x,y0+y] = color 
				if x0+x > 0 and y0-y > 0 and x0+x < canvasDim and y0-y < canvasDim:
					canvas[x0+x,y0-y] = color 
				if x0-x > 0 and y0+y > 0 and x0-x < canvasDim and y0+y < canvasDim:
					canvas[x0-x,y0+y] = color 
				if x0-x > 0 and y0-y > 0 and x0-x < canvasDim and y0-y < canvasDim:
					canvas[x0-x,y0-y] = color 

cdef void drawSquare(int x0, int y0, int dim, np.ndarray[np.uint8_t, ndim=2] canvas, int color):
	cdef int dim2 = <int> dim/2
	cdef int canvasDim = canvas.shape[0]
	cdef int x,y 
	for x in range(x0-dim2,x0+dim2):
		for y in range(y0-dim2,y0+dim2):
			if x >= 0 and x < canvasDim and y >= 0 and y < canvasDim:
				canvas[x,y] = color
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void drawSquare_optimized(int x0, int y0, int dim, np.uint8_t[:,:] canvas, int color, int canvasDim) nogil:
	cdef int dim2 = dim/2
	cdef int x,y 
	for x in range(x0-dim2,x0+dim2):
		for y in range(y0-dim2,y0+dim2):
			if x >= 0 and x < canvasDim and y >= 0 and y < canvasDim:
				canvas[x,y] = color

					
@cython.boundscheck(False)
@cython.wraparound(False)					
cpdef void drawPointLensers(np.ndarray[np.float64_t, ndim=2] stars, np.ndarray[np.uint8_t, ndim=2] canvas, object parameters):
	cdef int s
	cdef double x, y, r, m 
	cdef double w2 = parameters.canvasDim/2
	cdef double dTheta = parameters.dTheta.value 
	cdef int numstars = stars.shape[0]
	for s in range(0,numstars):
		x = stars[s,0]/dTheta + w2
		y = stars[s,1]/dTheta + w2
		m = stars[s,2]
		r = math.sqrt(m+2.0)
		drawSquare_optimized(<int>x,<int> y, <int> (r*2),canvas,2, <int> (w2*2))
