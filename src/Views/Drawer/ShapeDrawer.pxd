cimport numpy as np 

cpdef void drawCircle(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=2] canvas, int color)
cpdef void drawLine(int yIntercept, double slope, int yAx, np.ndarray[np.uint8_t, ndim=2] canvas, int color)
cpdef void drawSolidCircle(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=2] canvas, int color)
cpdef void drawPointLensers(np.ndarray[np.float64_t, ndim=2] stars, np.ndarray[np.uint8_t, ndim=2] canvas, object parameters)
cdef void drawSquare(int x0, int y0, int dim, np.ndarray[np.uint8_t, ndim=2] canvas, int color)