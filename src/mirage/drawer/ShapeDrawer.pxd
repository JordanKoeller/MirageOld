cimport numpy as np

cpdef void drawPointLensers(np.ndarray[np.float64_t, ndim=2] stars, np.ndarray[np.uint8_t, ndim=3] canvas, object model)
cdef void drawSquare_optimized(int x0, int y0, int dim, np.ndarray[np.uint8_t, ndim=3] canvas, int color, int canvasDim, object model)
cpdef void drawSquare(int x0, int y0, int dim, np.ndarray[np.uint8_t, ndim=3] canvas, int color, object model)
cpdef void drawSolidCircle(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=3] canvas, int color, object model)
cpdef void drawLine(int yIntercept, double slope, int yAx, np.ndarray[np.uint8_t, ndim=3] canvas, int color, object model)
cpdef void drawCircle(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=3] canvas, int color, object model)
cpdef void drawSolidCircle_Gradient(int x0, int y0, int r, np.ndarray[np.float64_t, ndim=2] canvas, double color)