#define PYOPENCL_DEFINE_CDOUBLE
#pragma OPENCL EXTENSION cl_khr_fp64 : enable
#define M_PI_2 1.5707963267948966


__kernel void ray_trace(
		__global const lenser_struct *stars,
		const int numStars, 
		const double Point_Constant,
		const double SIS_Constant,
		const double dL,
		const double dS,
		const double dLS,
		const int width, 
		const int height,
		const double dTheta,
		__global double *result_buf_x,
		__global double *result_buf_y)
	{
		int gid1 = get_global_id(0);
		int gid2 = get_global_id(1);
		int index = gid1*width + gid2;
		double incident_angle_x;
		double incident_angle_y;
		// double ray_at_galaxy_x;
		// double ray_at_galaxy_y;
		incident_angle_x = ((double) (gid1 - width / 2)) * dTheta;
		incident_angle_y = ((double) (gid2 - height / 2)) * dTheta;
		// ray_at_galaxy_x = incident_angle_x*dL;
		// ray_at_galaxy_y = incident_angle_y*dL;
		// double res_x;
		// double res_y;
		double deltaR_x;
		double deltaR_y;
		double r;
		// double random_double;
		// res_x = 0.0;
		// res_y = 0.0;
		result_buf_x[index] = 0.0;
		result_buf_y[index] = 0.0;
		r = 0.0;
		for (int i=0; i < numStars; i++)
		{
			if (stars[i].lenserType == 0) //Point mass lensing object
			{
				deltaR_x = (stars[i].x - incident_angle_x)*dL;
				deltaR_y = (stars[i].y - incident_angle_y)*dL;
				r = double(sqrt(float(deltaR_x*deltaR_x + deltaR_y*deltaR_y)));
				result_buf_x[index] += (deltaR_x*stars[i].mass/(r*r))*Point_Constant;
				result_buf_y[index] += (deltaR_y*stars[i].mass/(r*r))*Point_Constant;
			}
			else if (stars[i].lenserType == 1) //SIS Lensing body
			{

				// if (r < stars[i].radius)
				// {
					deltaR_x = stars[i].x - incident_angle_x;
					deltaR_y = stars[i].y - incident_angle_y;
					r = double(sqrt(float(deltaR_x*deltaR_x + deltaR_y*deltaR_y)));
					result_buf_x[index] += stars[i].mass * stars[i].mass * deltaR_x * SIS_Constant / r;
					result_buf_y[index] += stars[i].mass * stars[i].mass * deltaR_y * SIS_Constant / r;
				// }
			}
			else if (stars[i].lenserType == 2) //Shear lensing object. For simplicity, shear magnitude represented as mass
											   //Angle represented by radius variable
											   //x & y represent the center of the galaxy (for calculating theta and r)
			{
				deltaR_x = stars[i].x - incident_angle_x;
				deltaR_y = stars[i].y - incident_angle_y;
				r = double(sqrt(float(deltaR_x*deltaR_x + deltaR_y*deltaR_y)));
				result_buf_x[index] += stars[i].mass*r*((double) cos((float) ((float) 2*(stars[i].radius+M_PI_2)) - atan2((float) deltaR_y,(float) deltaR_x)));
				result_buf_y[index] += stars[i].mass*r*((double) sin((float) ((float) 2*(stars[i].radius+M_PI_2)) - atan2((float) deltaR_y,(float) deltaR_x)));

			}
		}
		result_buf_x[index] = (incident_angle_x*dL + ((incident_angle_x+(result_buf_x[index]))*dLS))/dS;
		result_buf_y[index] = (incident_angle_y*dL + ((incident_angle_y+(result_buf_y[index]))*dLS))/dS;
	}



