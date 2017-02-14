#ifdef cl_khr_fp64
	// typedef float double;
#elif defined(cl_amd_fp64)
	// typedef float double;
#else
	#pragma OPENCL EXTENSION cl_khr_fp64 : enable
	#define PYOPENCL_DEFINE_CDOUBLE
	// #define RAD_TO_ARCSEC 206264.80624709636
	// #define ARCSEC_TO_RAD 4.84813681109536e-06
	// #define RAD_TO_UAS 206264806247.09637
	// #define UAS_TO_RAD 4.848136811E-12
	#define M_PI_2 1.5707963267948966
	// typedef double double;
#endif

__kernel void ray_trace(
		__global const double *stars_mass,
		__global const double *stars_x,
		__global const double *stars_y,
		const int numStars, 
		const double POINT_CONSTANT,
		const double SIS_CONSTANT,
		const double shear_mag,
		const double shear_angle,
		const double velocityDispersion,
		const double dL,
		const double dS,
		const double dLS,
		const int width, 
		const int height,
		const double dTheta,
		const double centerX,
		const double centerY,
		__global double *result_buf_x,
		__global double *result_buf_y)
	{
		int gid1 = get_global_id(0);
		int gid2 = get_global_id(1);
		int index = gid1*width + gid2;
		double incident_angle_x;
		double incident_angle_y;
		incident_angle_x = (((double) (gid1 - width / 2)) * dTheta) + centerX; //Arcsec
		incident_angle_y = (((double) (gid2 - height / 2)) * dTheta) + centerY; //Arcsec
		double deltaR_x; //Arcsec
		double deltaR_y; //Arcsec
		double r;
		result_buf_x[index] = 0.0;
		result_buf_y[index] = 0.0;
		r = 0.0;
		for (int i=0; i < numStars; i++)
		{
		// if (stars[i].lenserType == 0) //Point mass lensing object
		// {
			deltaR_x = (stars_x[i] - incident_angle_x)*dL;
			deltaR_y = (stars_y[i] - incident_angle_y)*dL;
			r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
			result_buf_x[index] += (deltaR_x*stars_mass[i]/(r*r))*POINT_CONSTANT;
			result_buf_y[index] += (deltaR_y*stars_mass[i]/(r*r))*POINT_CONSTANT;
		// }
		// else if (stars[i].lenserType == 1) //SIS Lensing body
		// {
		}

			// if (r < stars[i].radius)
			// {
				deltaR_x = centerX - incident_angle_x;
				deltaR_y = centerY - incident_angle_y;
				r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
				result_buf_x[index] += velocityDispersion * velocityDispersion * deltaR_x * SIS_CONSTANT / r;
				result_buf_y[index] += velocityDispersion * velocityDispersion * deltaR_y * SIS_CONSTANT / r;
			// }
			// else if (stars[i].lenserType == 2) //Shear lensing object. For simplicity, shear magnitude represented as mass
			// 								   //Angle represented by radius variable
			// 								   //x & y represent the center of the galaxy (for calculating theta and r)
			// {
				// deltaR_x =  centerX - incident_angle_x; //Represents gammaX
				// deltaR_y = centerY - incident_angle_y; //Represents gammaY
				deltaR_x /= r;
				deltaR_y /= r;
				result_buf_x[index] += shear_mag*r*cos(2*(shear_angle+M_PI_2) - atan2(deltaR_y,deltaR_x));
				result_buf_y[index] += shear_mag*r*sin(2*(shear_angle+M_PI_2) - atan2(deltaR_y,deltaR_x));
				// result_buf_x[index] += stars_mass[i]*r*(shearX*deltaR_x+shearY*deltaR_y);
				// result_buf_x[index] += stars_mass[i]*r*(shearY*deltaR_x-shearX*deltaR_y);

		result_buf_x[index] = (incident_angle_x*dL + ((incident_angle_x+(result_buf_x[index]))*dLS))/dS;
		result_buf_y[index] = (incident_angle_y*dL + ((incident_angle_y+(result_buf_y[index]))*dLS))/dS;
		// result_buf_x[index] = 45.0;
		// result_buf_y[index] = 56.0;

}


