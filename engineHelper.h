// #define M_PI_2 1.5707963267948966
#include <math.h>
#include <stdio.h>
typedef double num;

typedef struct
{
	int lenserType;
	double mass;
	double x;
	double y;
	double radius;
} lenser_struct;


void ray_trace(
		void *starData,
		const int numStars, 
		const num Point_Constant,
		const num SIS_Constant,
		const num dL,
		const num dS,
		const num dLS,
		const int width, 
		const int height,
		const num dTheta,
		const num shiftX,
		const num shiftY,
		num *result_buf_x,
		num *result_buf_y)
	{
	printf("%lu\n\n\n",sizeof(dTheta));
	lenser_struct *stars = (lenser_struct*) starData;
	// printf("%d %d %d\n",numStars, width, height );
	for (int i=0;i < numStars;i++)
	{
		printf("%f %f %f\n",stars[i].x,stars[i].y,stars[i].mass);
	}
	for (int gid1 = 0; gid1 < width-1; gid1++)
	{
		for (int gid2 = 0; gid2 < height-1; gid2++)
		{
			// printf("%d\n",sizeof(stars[0]));
			// int gid1 = 0;
			// int gid2 = 0;
			int index = gid1*width + gid2;
			num incident_angle_x;
			num incident_angle_y;
			incident_angle_x = (((num) (gid1 - width / 2)) * dTheta) + shiftX;
			incident_angle_y = (((num) (gid2 - height / 2)) * dTheta) + shiftY;
			num deltaR_x;
			num deltaR_y;
			num r;
			result_buf_x[index] = 0.0;
			result_buf_y[index] = 0.0;
			r = 0.0;
			for (int i=0; i < numStars-1; i++)
			{
				if (stars[i].lenserType == 0) //Point mass lensing object
				{
					deltaR_x = (stars[i].x - incident_angle_x)*dL;
					deltaR_y = (stars[i].y - incident_angle_y)*dL;
					r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
					result_buf_x[index] += (deltaR_x*stars[i].mass/(r*r))*Point_Constant;
					result_buf_y[index] += (deltaR_y*stars[i].mass/(r*r))*Point_Constant;
				}
				else if (stars[i].lenserType == 1) //SIS Lensing body
				{

					// if (r < stars[i].radius)
					// {
						deltaR_x = stars[i].x - incident_angle_x;
						deltaR_y = stars[i].y - incident_angle_y;
						r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
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
					r = sqrt(deltaR_x*deltaR_x + deltaR_y*deltaR_y);
					result_buf_x[index] += stars[i].mass*r*(cos(2*(stars[i].radius+M_PI_2)) - atan2(deltaR_y,deltaR_x));
					result_buf_y[index] += stars[i].mass*r*(sin(2*(stars[i].radius+M_PI_2)) - atan2(deltaR_y,deltaR_x));

				}
			}
			result_buf_x[index] = (incident_angle_x*dL + ((incident_angle_x+(result_buf_x[index]))*dLS))/dS;
			result_buf_y[index] = (incident_angle_y*dL + ((incident_angle_y+(result_buf_y[index]))*dLS))/dS;
		}
	}
}
