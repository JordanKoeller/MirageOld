    cpdef ray_trace(self):
        '''Ray-traces the system on the CPU. Does not require openCL
        
        Must call reconfigure() before this method.
        '''
        begin = time.clock()
        cdef int height = self._parameters.canvasDim
        cdef int width = self._parameters.canvasDim
        height = height // 2
        width = width // 2
        cdef double dTheta = self._parameters.dTheta.value
        cdef np.ndarray[np.float64_t, ndim = 2] result_nparray_x = np.zeros((width * 2, height * 2), dtype=np.float64)
        cdef np.ndarray[np.float64_t, ndim = 2] result_nparray_y = np.zeros((width * 2, height * 2), dtype=np.float64)
        cdef double dS = self._parameters.quasar.angDiamDist.to('lyr').value
        cdef double dL = self._parameters.galaxy.angDiamDist.to('lyr').value
        cdef double dLS = self._parameters.dLS.to('lyr').value
        cdef np.ndarray[np.float64_t, ndim = 1] stars_mass, stars_x, stars_y
        cdef int numStars = 0
        if self._parameters.galaxy.percentStars > 0.0:
            stars_mass, stars_x, stars_y = self._parameters.galaxy.starArray
            numStars = len(stars_x)
        cdef double shearMag = self._parameters.galaxy.shear.magnitude
        cdef double shearAngle = self._parameters.galaxy.shear.angle.value
        cdef double centerX = self._parameters.galaxy.position.to('rad').x
        cdef double centerY = self._parameters.galaxy.position.to('rad').y
        cdef double sis_constant =     np.float64(4 * math.pi * self._parameters.galaxy.velocityDispersion ** 2 * (const.c ** -2).to('s2/km2').value * dLS / dS)
        cdef double point_constant = (4 * const.G / const.c / const.c).to("lyr/solMass").value * dLS / dS / dL
        cdef double pi2 = math.pi / 2
        cdef int x, y, i
        cdef double incident_angle_x, incident_angle_y, r, deltaR_x, deltaR_y, phi
        for x in prange(0, width * 2, 1, nogil=True, schedule='static', num_threads=self.core_count):
            for y in range(0, height * 2):
                incident_angle_x = (x - width) * dTheta
                incident_angle_y = (height - y) * dTheta

                for i in range(numStars):
                    deltaR_x = incident_angle_x - stars_x[i]
                    deltaR_y = incident_angle_y - stars_y[i]
                    r = deltaR_x * deltaR_x + deltaR_y * deltaR_y
                    if r != 0.0:
                        result_nparray_x[x, y] += deltaR_x * stars_mass[i] * point_constant / r;
                        result_nparray_y[x, y] += deltaR_y * stars_mass[i] * point_constant / r;                
#                 
                # SIS
                deltaR_x = incident_angle_x - centerX
                deltaR_y = incident_angle_y - centerY
                r = sqrt(deltaR_x * deltaR_x + deltaR_y * deltaR_y)
                if r != 0.0:
                    result_nparray_x[x, y] += deltaR_x * sis_constant / r 
                    result_nparray_y[x, y] += deltaR_y * sis_constant / r

                # Shear
                phi = 2 * (pi2 - shearAngle) - CMATH.atan2(deltaR_y, deltaR_x)
                result_nparray_x[x, y] += shearMag * r * CMATH.cos(phi)
                result_nparray_y[x, y] += shearMag * r * CMATH.sin(phi)
                result_nparray_x[x, y] = deltaR_x - result_nparray_x[x, y]
                result_nparray_y[x, y] = deltaR_y - result_nparray_y[x, y]

