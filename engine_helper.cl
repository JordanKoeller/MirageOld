#ifdef cl_khr_fp64
	typedef float num;
#elif defined(cl_amd_fp64)
	typedef float num;
#else
	#pragma OPENCL EXTENSION cl_khr_fp64 : enable
	#define PYOPENCL_DEFINE_CDOUBLE
	// #define RAD_TO_ARCSEC 206264.80624709636
	// #define ARCSEC_TO_RAD 4.84813681109536e-06
	// #define RAD_TO_UAS 206264806247.09637
	// #define UAS_TO_RAD 4.848136811E-12
	#define M_PI_2 1.5707963267948966
	typedef double num;
#endif

__kernel void ray_trace(
		__global const lenser_struct *stars,
		const int numStars, 
		const num Point_Constant,
		const num SIS_Constant,
		const num shearX,
		const num shearY,
		const num velocityDispersion,
		const num dL,
		const num dS,
		const num dLS,
		const int width, 
		const int height,
		const num dTheta,
		const num centerX,
		const num centerY,
		__global num *result_buf_x,
		__global num *result_buf_y)
	{
		int gid1 = get_global_id(0);
		int gid2 = get_global_id(1);
		int index = gid1*width + gid2;
		num incident_angle_x;
		num incident_angle_y;
		incident_angle_x = (((num) (gid1 - width / 2)) * dTheta) + centerX; //Arcsec
		incident_angle_y = (((num) (gid2 - height / 2)) * dTheta) + centerY; //Arcsec
		num deltaR_x; //Arcsec
		num deltaR_y; //Arcsec
		num r;
		result_buf_x[index] = 0.0;
		result_buf_y[index] = 0.0;
		r = 0.0;
		for (int i=0; i < numStars; i++)
		{
			if (stars[i].lenserType == 0) //Point mass lensing object
			{
				deltaR_x = (stars[i].x - incident_angle_x)*dL;
				deltaR_y = (stars[i].y - incident_angle_y)*dL;
				r = num(sqrt(float(deltaR_x*deltaR_x + deltaR_y*deltaR_y)));
				result_buf_x[index] += (deltaR_x*stars[i].mass/(r*r))*Point_Constant;
				result_buf_y[index] += (deltaR_y*stars[i].mass/(r*r))*Point_Constant;
			}
			else if (stars[i].lenserType == 1) //SIS Lensing body
			{

				// if (r < stars[i].radius)
				// {
					deltaR_x = stars[i].x - incident_angle_x;
					deltaR_y = stars[i].y - incident_angle_y;
					r = num(sqrt(float(deltaR_x*deltaR_x + deltaR_y*deltaR_y)));
					result_buf_x[index] += stars[i].mass * stars[i].mass * deltaR_x * SIS_Constant / r;
					result_buf_y[index] += stars[i].mass * stars[i].mass * deltaR_y * SIS_Constant / r;
				// }
			}
			else if (stars[i].lenserType == 2) //Shear lensing object. For simplicity, shear magnitude represented as mass
											   //Angle represented by radius variable
											   //x & y represent the center of the galaxy (for calculating theta and r)
			{
				deltaR_x = stars[i].x - incident_angle_x; //Represents gammaX
				deltaR_y = stars[i].y - incident_angle_y; //Represents gammaY
				r = num(sqrt(float(deltaR_x*deltaR_x + deltaR_y*deltaR_y)));
				deltaR_x /= r;
				deltaR_y /= r;
				result_buf_x[index] += stars[i].mass*r*((num) cos((float) ((float) 2*(stars[i].radius+M_PI_2)) - atan2((float) deltaR_y,(float) deltaR_x)));
				result_buf_y[index] += stars[i].mass*r*((num) sin((float) ((float) 2*(stars[i].radius+M_PI_2)) - atan2((float) deltaR_y,(float) deltaR_x)));
				// result_buf_x[index] += stars[i].mass*r*(shearX*deltaR_x+shearY*deltaR_y);
				// result_buf_x[index] += stars[i].mass*r*(shearY*deltaR_x-shearX*deltaR_y);

			}
		}
		result_buf_x[index] = (incident_angle_x*dL + ((incident_angle_x+(result_buf_x[index]))*dLS))/dS;
		result_buf_y[index] = (incident_angle_y*dL + ((incident_angle_y+(result_buf_y[index]))*dLS))/dS;
	}



