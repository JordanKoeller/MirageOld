cimport numpy as np 

cdef angleToPixel(object parameters, object angles):
	cdef np.ndarray[np.float64_t,ndim=2] angleArray
	cdef double canvasDim = <double> parameters.canvasDim
	cdef double dTheta = parameters.dTheta.to('rad').value

	if isinstance(angles,np.ndarray):
		angleArray = angles
		angleArray[:,0] = (angleArray[:,0]/dTheta)+canvasDim/2
		angleArray[:,1] = canvasDim/2 - (angleArray[:,1]/dTheta)
cdef pixelToAngle(object parameters, object input):
