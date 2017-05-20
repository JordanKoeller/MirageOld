#ifdef cl_khr_fp64
	// typedef float double;
#elif defined(cl_amd_fp64)
	// typedef float double;
#else
	#pragma OPENCL EXTENSION cl_khr_fp64 : enable
	#define PYOPENCL_DEFINE_CDOUBLE
	#define M_PI_2 1.5707963267948966
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

		// Setup
		// Note: all distances are measured in radians, so that trig at the end is natural
		int gid1 = get_global_id(0);
		int gid2 = get_global_id(1);
		int index = gid1*width + gid2;
		double incident_angle_x;
		double incident_angle_y;
		incident_angle_x = ((double) (gid1 - width / 2)) * dTheta;
		incident_angle_y = ((double) (gid2 - height / 2)) * dTheta;
		double deltaR_x;
		double deltaR_y;
		double r;
		double phi;
		result_buf_x[index] = 0.0;
		result_buf_y[index] = 0.0;
		r = 0.0;
		//For Loop for  all the stars
		for (int i=0; i < numStars; i++)
		{
			deltaR_x = (stars_x[i] - incident_angle_x)*dL;
			deltaR_y = (stars_y[i] - incident_angle_y)*dL;
			r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
			result_buf_x[index] += (deltaR_x*stars_mass[i]/(r*r))*POINT_CONSTANT;
			result_buf_y[index] += (deltaR_y*stars_mass[i]/(r*r))*POINT_CONSTANT;
		}
		// Lensing from SIS
		deltaR_x =  incident_angle_x - centerX;
		deltaR_y =  incident_angle_y - centerY;
		r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
		result_buf_x[index] += velocityDispersion * velocityDispersion * (-deltaR_x) * SIS_CONSTANT / r;
		result_buf_y[index] += velocityDispersion * velocityDispersion * (-deltaR_y) * SIS_CONSTANT / r;

		// Lensing from shear
		phi = 2*(shear_angle+M_PI_2) - atan2(deltaR_y,deltaR_x);
		result_buf_x[index] += shear_mag*r*cos(phi);
		result_buf_y[index] += shear_mag*r*sin(phi);
		result_buf_x[index] = (incident_angle_x*dL + ((incident_angle_x+(result_buf_x[index]))*dLS))/dS;
		result_buf_y[index] = (incident_angle_y*dL + ((incident_angle_y+(result_buf_y[index]))*dLS))/dS;

}


