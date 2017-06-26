#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>
#include <unordered_map>
#include <unordered_set>
#include <climits>

using namespace std;

typedef unsigned int Index;



inline double isLeft(const double* x,const double* y,const int &p0,const int &p1,const double* p2);
bool project(const double* x,const double* y,const int &vStart,const int &vEnd, double &cx, double &cy, double &r2);
inline double hypot2(const double& x1,const double& y1,const double& x2,const double& y2);
inline tuple<int,int,int,int> getCorners(const int &tl,const int &width);
bool winding_algorithm(const double * x,const double * y,const int * V,const double* P);
bool intersect(const double* x, const double* y, const int &tlx, const int &tly, const int &width, const double &qx, const double &qy, const double &qr);
inline double isLeft(const double* x,const double* y,const int &p0,const int &p1,const double* p2);
double sourcePlaneArea(double *x, double* y, const int &width);
vector<pair<int,int>> query_data(const double* x,const double* y,const int width,const double qx,const double qy,const double r);

double sourcePlaneArea(double *x, double* y, const int &width)
{
	double ret = 0.0;
	
}




bool project(const double* x,const double* y,const int &vStart,const int &vEnd, const double &cx, const double &cy,const double &r2)
{
	double C[2];
	double A[2];
	A[0] = x[vEnd]-x[vStart];
	A[1] = y[vEnd]-y[vStart];
	C[0] = cx-x[vStart];
	C[1] = cy-y[vStart];
	double C2 = (C[0])*(C[0])+(C[1])*(C[1]);
	double A2 = ((A[0])*(A[0])+(A[1])*(A[1]));
	double dot = (C[0])*(A[0])+(C[1])*(A[1]);
	double CCos = (dot*dot/A2);
	if (CCos > A2)
	{
		return false;
	}
	else if (C2 - CCos <= r2)
	{
		return true;
	}
	else {
		return false;
	}
}

inline double hypot2(const double& x1,const double& y1,const double& x2,const double& y2)
{
	double dx = x2 - x1;
	double dy = y2-y1;
	return dx*dx+dy*dy;
}

inline tuple<int,int,int,int> getCorners(const int &tl,const int &width)
{
	int tr = (tl+1);
	int bl = (tl+width);
	int br = (tl+(width+1));
	return make_tuple(tl,tr,bl,br);
}

bool winding_algorithm(const double * x,const double * y,const int * V,const double* P)
{
	//Arguments are as follows:
	/* V : double**. 5-long array of double*, where each element is a pointer to the next corner of a 4-sided polygon.
			for arbitrary i, V[i+1] correlates to the y-coordinate of the corner.
	   P : double*. Pointer to the point to check if within the shape described by V. P[0] = P.x, P[1] = P.y
	*/
	int wn = 0;
	for (int i=0;i < 4;i++)
	{
		// cout << V[i][0] << "," << V[i][1] << "\n";
		if (y[V[i]] <= P[1])
		{
			if (y[V[i+1]] > P[1])
			{
				if (isLeft(x,y,V[i],V[i+1],P) > 0)
				{
					wn++;
				}
			}
		}
		else
		{
			if (y[V[i+1]] <= P[1])
			{
				if (isLeft(x,y,V[i],V[i+1],P) < 0)
				{
					wn--;
				}
			}
		}
	}
	if (wn != 0)
	{
		return true;
	}
	else
	{
		return false;
	}
	
}

bool intersect(const double* x, const double* y, const int tl, const int &width, const double &qx, const double &qy, const double &qr)
{
	double r2 = qr*qr;
	int V [5];
	auto corners = getCorners(tl, width);
	V[0] = get<0>(corners); //tl
	V[1] = get<1>(corners); //tr
	V[2] = get<3>(corners); //br
	V[3] = get<2>(corners); //bl
	V[4] = get<0>(corners);
	double P[2];
	P[0] = qx;
	P[1] = qy;
	// cout << "Made V and P \n";
	//Check if a corner is within the circle
	if (hypot2(x[V[0]],y[V[0]],qx,qy) <= r2 ||
		hypot2(x[V[1]],y[V[1]],qx,qy) <= r2 ||
		hypot2(x[V[2]],y[V[2]],qx,qy) <= r2 ||
		hypot2(x[V[3]],y[V[3]],qx,qy) <= r2)
	{
		return true;
	}
	// cout << "Hypot checked\"
	// return false;

	//Check if circle is within the polygon using the Winding Number Algorithm
	// if (winding_algorithm(x,y,V, P))
	// {
	// 	return true;
	// }

	// // Check if circle intersects an edge of the shape
	// if (project(x,y,V[1],V[0],qx,qy,r2) ||
	// 	project(x,y,V[3],V[1],qx,qy,r2) ||
	// 	project(x,y,V[2],V[3],qx,qy,r2) ||
	// 	project(x,y,V[0],V[2],qx,qy,r2))
	// {
	// 	return true;
	// }
	return false;
}

inline double isLeft(const double* x,const double* y,const int &p0,const int &p1,const double* p2)
{
	return ((x[p1] - x[p0])*(p2[1]-y[p0])-(p2[0]-x[p0])*(y[p1]-y[p0]));
}








vector<pair<int,int>> query_shape(const double* x,const double* y,const int width,const double qx,const double qy,const double r)
{
	// double* x {new double[width*width]};
	// double* y {new double[width*width]};
	// for (int k = 0; k < width*width; ++k)
	// {
	// 	x[k] = xx[k];
	// 	y[k] = yy[k];
	// }

	vector<pair<int,int>> ret;
	#pragma omp parallel
	{
		vector<pair<int,int>> private_ret;
		#pragma omp for nowait
		for (int i=0;i < width-1; ++i)
		{
			for (int j = 0; j < width-1; ++j)
			{
				if (intersect(x,y,i*width+j,width,qx,qy,r))
				{

					private_ret.push_back(make_pair(i,j));
				}
			}
		}
		#pragma omp critical
		ret.insert(ret.end(), private_ret.begin(), private_ret.end());
	}

	// delete [] x;
	// delete [] y;
	return ret;
}