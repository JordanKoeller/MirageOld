from Views.Drawer.Drawer cimport ImageDrawer
import numpy as np 
cimport numpy as np 
import math


cdef class ShapeDrawer(ImageDrawer):

	def __init__(self,signal):
		ImageDrawer.__init__(self,signal)

	cdef void drawCircle(self, int x0, int y0, int r, np.ndarray[np.uint8_t,ndim=2] canvas):
		cdef int x = abs(r)
		cdef int y = 0
		cdef int err = 0
		cdef int canvasDim = canvas.shape[0]
		with nogil:
			while x >= y:
				if x0 + x > 0 and y0 + y > 0 and x0 + x < canvasDim and y0 + y < canvasDim:
						canvas[x0 + x, y0 + y] = 3
				if x0 + y > 0 and y0 + x > 0 and x0 + y < canvasDim and y0 + x < canvasDim:
						canvas[x0 + y, y0 + x] = 3
				if x0 - y > 0 and y0 + x > 0 and x0 - y < canvasDim and y0 + x < canvasDim:
						canvas[x0 - y, y0 + x] = 3
				if x0 - x > 0 and y0 + y > 0 and x0 - x < canvasDim and y0 + y < canvasDim:
						canvas[x0 - x, y0 + y] = 3
				if x0 - x > 0 and y0 - y > 0 and x0 - x < canvasDim and y0 - y < canvasDim:
						canvas[x0 - x, y0 - y] = 3
				if x0 - y > 0 and y0 - x > 0 and x0 - y < canvasDim and y0 - x < canvasDim:
						canvas[x0 - y, y0 - x] = 3
				if x0 + y > 0 and y0 - x > 0 and x0 + y < canvasDim and y0 - x < canvasDim:
						canvas[x0 + y, y0 - x] = 3
				if x0 + x > 0 and y0 - y > 0 and x0 + x < canvasDim and y0 - y < canvasDim:
						canvas[x0 + x, y0 - y] = 3
				if err <= 0:
					y += 1
					err += 2*y + 1
				if err > 0:
					x -= 1
					err -= 2*x + 1
	cdef void drawLine(self, int yIntercept, double slope, int yAx, np.ndarray[np.uint8_t, ndim=2] canvas):
		cdef int width = canvas.shape[0]
		cdef int height = canvas.shape[1]
		cdef int x = yAx
		cdef int y = yIntercept
		cdef int i = 0
		for i in range(0,width):
			y = yIntercept + int((i - yAx)*slope)
			if y > -1 and y < height:
				canvas[height - 1 - y,i] = 3

