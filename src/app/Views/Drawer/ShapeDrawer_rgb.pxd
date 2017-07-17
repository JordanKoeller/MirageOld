cimport numpy as np

cpdef void drawCircle_rgb(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=3] canvas, int color)
cpdef void drawLine_rgb(int yIntercept, double slope, int yAx, np.ndarray[np.uint8_t, ndim=3] canvas, int color)
cpdef void drawSolidCircle_rgb(int x0, int y0, int r, np.ndarray[np.uint8_t, ndim=3] canvas, int color)
cpdef void drawPointLensers_rgb(np.ndarray[np.float64_t, ndim=2] stars, np.ndarray[np.uint8_t, ndim=3] canvas, object parameters)
cpdef void drawSquare_rgb(int x0, int y0, int dim, np.ndarray[np.uint8_t, ndim=3] canvas, int color)
cdef void drawSquare_optimized_rgb(int x0, int y0, int dim, np.ndarray[np.uint8_t, ndim=3] canvas, int color, int canvasDim)