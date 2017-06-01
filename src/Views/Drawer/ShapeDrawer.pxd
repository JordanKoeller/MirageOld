from Views.Drawer.Drawer cimport ImageDrawer
cimport numpy as np 

cdef class ShapeDrawer(ImageDrawer):
	cdef void drawCircle(self, int x0, int y0, int r, np.ndarray[np.uint8_t,ndim=2] canvas)

	cdef void drawLine(self, int yIntercept, double slope, int yAx, np.ndarray[np.uint8_t, ndim=2] canvas)
