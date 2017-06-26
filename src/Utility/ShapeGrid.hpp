#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>
#include <unordered_map>
#include <unordered_set>
#include <climits>
#include <queue>

using namespace std;


class ShapeGrid
{
	class Node;
public:
	typedef unsigned int Index;
	friend class ShapeGrid::Node;

private:
	double* rawData;
	double* shapeAreas;

	class PqComp
	{
	public:
		PqComp()=default;
		bool operator() (const double* a, const double* b)
		{
			return atan2(b[1],b[0]) > atan2(a[1],a[0]);

		}
	};

	inline static double hypot2( double& x1,  double& y1,  double& x2,  double& y2)
	{
		double dx = x2 - x1;
		double dy = y2 - y1;
		return dx*dx+dy*dy;
	}


	static bool lineCircleIntersection(double & r, double * hk, double * line, double* ret1, double* ret2)
	{
		double A = line[1]*line[1]+line[0]*line[0];
		double B = 2*line[1]*(hk[0]-line[2])-2*hk[1]*line[0]*line[0];
		double C = line[0]*line[0]*hk[0]*hk[0]+(line[2]-hk[0])*(line[2]-hk[0])-r*r*line[0]*line[0];
		bool flag1 = false;
		bool flag2 = false;
		try
		{		
			ret1[1] = (-B+sqrt(B*B-4*A*C))/(2*A);
			ret1[0] = (line[2] - line[1]*ret1[1])/line[0];
		}
		catch (...)
		{
			flag1 = false;
		}
		try
		{
			ret2[1] = (-B-sqrt(B*B-4*A*C))/(2*A);
			ret2[0] = (line[2] - line[1]*ret2[1])/line[0];
		}
		catch (...)
		{
			flag2 = false;
		}
		return flag1 || flag2;
	}

	inline static bool intersectSegment(double* v1, double* v2, double* pt)
	{
		return (min(v1[0],v2[0]) <= pt[0] && max(v1[0],v2[0]) >= pt[0] &&
				min(v1[1],v2[1]) <= pt[1] && max(v1[1],v2[1]) >= pt[1]);
	}

	inline static double areaOfTriangle(double*p1, double* p2, double* p3)
	{
		double area = 0.0;
		area += p1[0]*p2[1];
		area += p2[0]*p3[1];
		area += p3[0]*p1[1];
		area -= p1[1]*p2[0];
		area -= p2[1]*p3[0];
		area -= p3[1]*p1[0];
		return abs(area*0.5);
	}


	static double polyCircleOverlap(double *v1, double* v2, double*v3, double * hk, double & r)
	{ //VERTICES IS 3 LONG
		double*vertices[3] {v1,v2,v3};
		priority_queue<double*,vector<double*>,PqComp> pq;
		double line[3];
		double intersect1[2] {0.0,0.0};
		double intersect2[2] {0.0,0.0};
		for (int i = 0; i < 3; ++i)
		{
			if (hypot2(vertices[i][0],vertices[i][1],hk[0],hk[1]) <= r*r)
			{
				double pushable[2] {vertices[i][0] - hk[0], vertices[i][1] - hk[1]};
				pq.push(pushable);
			}
			getLine(vertices[i],vertices[(i+1)%3],line);
			if (lineCircleIntersection(r, hk, line,intersect1,intersect2))
			{
				if(intersectSegment(vertices[i],vertices[i+1],intersect1))
				{
					intersect1[0] -= hk[0];
					intersect1[1] -= hk[1];
					pq.push(intersect1);
				}
				if (intersectSegment(vertices[i],vertices[i+1],intersect2))
				{
					intersect2[0] -= hk[0];
					intersect2[1] -= hk[1];
					pq.push(intersect2);
				}
			}
		}

		if (pq.size() == 3)
		{
			return areaOfTriangle(vertices[0],vertices[1],vertices[2]);
			//return area of polygon
		}
		else if (pq.size() == 0)
		{
			return M_PI*r*r;
			//return area of circle
		}
		else if (pq.size() == 2)
		{
			double chord[3];
			auto tmp1 = pq.top();
			pq.pop();
			auto tmp2 = pq.top();
			getLine(tmp1,tmp2,chord);
			for (int i = 0; i < 3; ++i)
			{
				if (vertices[i] != tmp1 && vertices[i] != tmp2)
				{
					double ctrSide = isLeft(tmp1,tmp2,hk);
					double otherSide = isLeft(tmp1,tmp2,vertices[i]);
					double theta = atan2(tmp2[1],tmp2[0])-atan2(tmp1[1],tmp1[0]);
					double area = r*r*(theta-abs(sin(theta)))/2;
					if (ctrSide*otherSide >= 0)
					{
						//Same side, so subtract area of hemisphere
						return M_PI*r*r - area;
					}
					else
					{
						return M_PI*r*r + area;
						//add area of hemisphere
					}
				}
			}
			return 0.0;
		}
		else {
			vector<double*> pts;
			while (!pq.empty())
			{
				pts.push_back(pq.top());
				pq.pop();
			}
			return areaOfPolygon(pts);
			//Calculate area of the polygon
		}
	}


	static double areaOfPolygon(vector<double*> &pts)
	{
		double area = 0.0;
		for (int i = 0; i < pts.size(); ++i)
		{
			int j = (i+1)%pts.size();
			area += pts[i][0]*pts[j][1] - pts[j][0]*pts[i][1];
			/* code */
		}
		return 0.5*abs(area);
	}

	static double getAreaofQuad(double* p1, double* p2, double* p3, double* p4)
	{
		double intersection[2];
		if (getIntersection(p1,p2,p3,p4, intersection))
		{ //Shape goes p1 ->  intersection -> p4 -> p1, p3 -> intersection -> p2 ->p3
			double area1 = 0.0;
			double area2 = 0.0;
			area1 += p1[0]*intersection[1];
			area1 += intersection[0]*p4[1];
			area1 += p4[0]*p1[1];
			area1 -= p1[1]*intersection[0];
			area1 -= intersection[1]*p4[0];
			area1 -= p4[1]*p1[0];

			area2 += p3[0]*intersection[1];
			area2 += intersection[0]*p2[1];
			area2 += p2[0]*p3[1];
			area2 -= p3[1]*intersection[0];
			area2 -= intersection[1]*p2[0];
			area2 -= p2[1]*p3[0];

			return -0.5*(abs(area1) + abs(area2));

		}
		else if (getIntersection(p1,p4,p2,p3, intersection))
		{
			//goes p1 -> p3 -> intersection -> p1
			//goes p2 -> intersection -> p4 -> p2
			double area1 = 0.0;
			double area2 = 0.0;
			area1 += p1[0]*p3[1];
			area1 += p3[0]*intersection[1];
			area1 += intersection[0]*p1[1];
			area1 -= p1[1]*p3[0];
			area1 -= p3[1]*intersection[0];
			area1 -= intersection[1]*p1[0];

			area2 += p2[0]*intersection[1];
			area2 += intersection[0]*p4[1];
			area2 += p4[0]*p2[1];
			area2 -= p2[1]*intersection[0];
			area2 -= intersection[1]*p4[0];
			area2 -= p4[1]*p2[0];
			return -0.5*(abs(area1) + abs(area2));
		}
		else
		{
			double area = 0.0;
			area += p1[0]*p2[1];
			area += p2[0]*p3[1];
			area += p3[0]*p4[1];
			area += p4[0]*p1[1];
			area -= p1[1]*p2[0];
			area -= p2[1]*p3[0];
			area -= p3[1]*p4[0];
			area -= p4[1]*p1[0];
			return abs(0.5*area);
		}

	}

	static void getLine(double * p1, double * p2, double* ret)
	{
		ret[0] = p2[1] - p1[1];
		ret[1] = p1[0]-p2[0];
		ret[2] = ret[0]*p1[0]+ret[1]*ret[1];
	}

	static bool lineIntersects(double * a1, double * a2, double * b1, double * b2)
	{
		double lineA [3];
		double lineB [3];
		getLine(a1,a2,lineA);
		getLine(b1,b2,lineB);
		double det = lineA[0]*lineB[1] - lineB[0]*lineA[1];
		if (det == 0)
		{
			return false;
		}
		else {
			double x = (lineB[1]*lineA[2] - lineA[0]*lineB[2])/det;
			double y = (lineA[0]*lineB[2] - lineB[0]*lineA[2])/det;
			return (min(a1[0],a2[0]) <= x && max(a1[0],a2[0]) >= x &&
					min(b1[0],b2[0]) <= x && max(b1[0],b2[0]) >= x &&
					min(a1[1],a2[1]) <= y && max(a1[1],a2[1]) >= y &&
					min(b1[1],b2[1]) <= y && max(b1[1],b2[1]) >= y);
		}
	}

	static bool getIntersection(double * a1, double * a2, double * b1, double * b2, double * ret)
	{
		double lineA [3];
		double lineB [3];
		getLine(a1,a2,lineA);
		getLine(b1,b2,lineB);
		double det = lineA[0]*lineB[1] - lineB[0]*lineA[1];
		ret[0] = (lineB[1]*lineA[2] - lineA[0]*lineB[2])/det;
		ret[1] = (lineA[0]*lineB[2] - lineB[0]*lineA[2])/det;
		if (det == 0)
		{
			return false;
		}
		else
		{
			return (min(a1[0],a2[0]) <= ret[0] && max(a1[0],a2[0]) >= ret[0] &&
					min(b1[0],b2[0]) <= ret[0] && max(b1[0],b2[0]) >= ret[0] &&
					min(a1[1],a2[1]) <= ret[1] && max(a1[1],a2[1]) >= ret[1] &&
					min(b1[1],b2[1]) <= ret[1] && max(b1[1],b2[1]) >= ret[1]);
		}
	}

	inline pair<int,int> pos_from_pointer(Index &ind)
	{
		int diff = ind/2;
		int y = diff % width;
		int x = diff / width;
		return make_pair(x,y);
	}

	inline void getCorners(Index &tl,double** ret)
	{
		ret[0] = rawData + tl;
		ret[1] = rawData + (tl+2);
		ret[2] = rawData + (tl+2*(width+1));
		ret[3] = rawData + (tl+2*width);
		ret[4] = ret[0];
	}

	inline pair<double,double> getIndices( double *x, double *y)
	{
		double xx  = ((*x) - tlx)/NODE_WIDTH;
		double yy  = ((*y) - tly)/NODE_HEIGHT;
		return make_pair(xx,yy);				
	}

	inline Index contigIndex(Index &i, Index &j)
	{
		return 2*(i*width+j);
	}

	inline static bool project(double* vStart, double*vEnd, double &cx, double &cy, double &r2)
	{
		double C[2];
		double A[2];
		A[0] = vEnd[0]-vStart[0];
		A[1] = vEnd[1]-vStart[1];
		C[0] = cx-vStart[0];
		C[1] = cy-vStart[1];
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

	inline static bool winding_algorithm(double ** V, double* P)
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
			if (V[i][1] <= P[1])
			{
				if (V[i+1][1] > P[1])
				{
					if (isLeft(V[i],V[i+1],P) > 0)
					{
						wn++;
					}
				}
			}
			else
			{
				if (V[i+1][1] <= P[1])
				{
					if (isLeft(V[i],V[i+1],P) < 0)
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

	bool intersect(Index &tl, double &x, double &y, double &r2)
	{
		double *V[5];
		getCorners(tl,V); // tl tr bl br
		double P[2];
		P[0] = x;
		P[1] = y;
		//Check if a corner is within the circle
		if (hypot2(V[0][0],V[0][1],x,y) <= r2 ||
			hypot2(V[1][0],V[1][1],x,y) <= r2 ||
			hypot2(V[2][0],V[2][1],x,y) <= r2 ||
			hypot2(V[3][0],V[3][1],x,y) <= r2)
		{
			return true;
		}
		//Check if circle is within the polygon using the Winding Number Algorithm
		else if (winding_algorithm(V, P))
		{
			return true;
		}

		// Check if circle intersects an edge of the shape
		else if (project(V[0],V[1],x,y,r2) ||
			project(V[1],V[3],x,y,r2) ||
			project(V[3],V[2],x,y,r2) ||
			project(V[2],V[1],x,y,r2))
		{
			return true;
		}
		else{
			
			return false;
		}


	}

	inline static double isLeft(double* p0, double* p1, double* p2)
	{
		return ((p1[0] - p0[0])*(p2[1]-p0[1])-(p2[0]-p0[0])*(p1[1]-p0[1]));
	}

	bool grid_overlap(int &i, int &j, Index &tl)
	{
		double *shape[5];
		getCorners(tl,shape);
		double *grid [5];
		double gridRaw [10];
		gridRaw[0] = i*NODE_WIDTH + tlx; //tl
		gridRaw[1] = j*NODE_HEIGHT + tly;

		gridRaw[2] = (i+1)*NODE_WIDTH + tlx; //tr
		gridRaw[3] = j*NODE_HEIGHT + tly;

		gridRaw[4] = (i+1)*NODE_WIDTH + tlx; //br
		gridRaw[5] = (j+1)*NODE_HEIGHT + tly;

		gridRaw[6] = (i)*NODE_WIDTH + tlx; //bl
		gridRaw[7] = (j+1)*NODE_HEIGHT + tly;

		gridRaw[8] = i*NODE_WIDTH + tlx; //tl
		gridRaw[9] = j*NODE_HEIGHT + tly;

		grid[0] = gridRaw;
		grid[1] = gridRaw+2;
		grid[2] = gridRaw+4;
		grid[3] = gridRaw+6;
		grid[4] = gridRaw+8;
		for (int k = 0; k < 4; k++)
		{
			if (winding_algorithm(shape,grid[k])  ||  winding_algorithm(grid,shape[k]))
			{
				return true;	
			}
		}
		for (int k=0; k < 4; k++)
		{
			for (int l = 0; l < 4; l++)
			{
				if (lineIntersects(shape[k],shape[k+1],grid[l],grid[l+1]))
				{
					return true;
				}
			}
		}
		return false;
	}


	void constructGrid( double& x1,  double& y1,  double& x2,  double& y2,  int &node_count)
	{
		tlx = x1;
		tly = y1;
		int rootNodes = (int) sqrt(node_count);
		NODE_HEIGHT = (y2 - y1)/ (double) rootNodes;
		NODE_WIDTH = (x2 - x1)/(double) rootNodes;
		data = vector<vector<Node>>(rootNodes,vector<Node>(rootNodes));

	}

	struct Node
	{
		std::vector<Index> node_data;
		void addData(Index &tl)
		{
			node_data.push_back(tl);
		}
		void queryNode( double& ptx,  double& pty, double &radius, ShapeGrid * outer, unordered_set<Index> & ret) 
		{
			for (size_t i = 0; i < node_data.size(); ++i)
			{
				if (outer->intersect(node_data[i],ptx,pty,radius))
				{
					ret.insert(node_data[i]);
				}
			}
			return;
		}
		void copyNodeData(unordered_set<Index> & ret)
		{
			ret.insert(node_data.begin(),node_data.end());
		}
		Node()=default;
		~Node()=default;

		
	};
	double NODE_WIDTH;
	double NODE_HEIGHT;
	double tlx;
	double tly;
	unsigned int sz;
	Index width;
	Index height;
	vector<vector<Node>> data;

public:

	ShapeGrid(double* xx,double* yy, int h, int w, int ndim, int node_count)
	{
		width = (Index) w;
		height = (Index) h;
		rawData = new double[w*h*2];
		shapeAreas = new double[w*h];
		double minX = DBL_MAX;
		double minY = DBL_MAX;
		double maxX = DBL_MIN;
		double maxY = DBL_MIN;
		Index i = 0;
		for (Index x = 0; x < width; ++x)
		{
			for (Index y = 0; y < height; ++y)
			{
				i = contigIndex(x,y);
				minX = min(minX,xx[i/2]);
				minY = min(minY,yy[i/2]);
				maxX = max(maxX,xx[i/2]);
				maxY = max(maxY,yy[i/2]);
				rawData[i] = xx[i/2];
				rawData[i+1] = yy[i/2];
			}
		}
		constructGrid(minX,minY,maxX,maxY,node_count);
		for (Index x = 0; x < width-1; ++x)
		{
			for (Index y = 0; y < height-1; ++y)
			{
				auto cInd = contigIndex(x,y);
				insert(cInd);
			}
		}
	}

	ShapeGrid()=default;

	ShapeGrid(const ShapeGrid &other)
	{
		NODE_WIDTH = other.NODE_WIDTH;
		NODE_HEIGHT = other.NODE_HEIGHT;
		tlx = other.tlx;
		tly = other.tly;
		sz = other.sz;
		width = other.width;
		height = other.height;
		data = other.data;
		rawData = new double[height*width*2];
		shapeAreas = new double[height*width];
		for (Index i = 0; i < width*height*2; ++i)
		{
			rawData[i] = other.rawData[i];
			shapeAreas[i/2] = other.shapeAreas[i/2];
		}
	}

	ShapeGrid &operator=(const ShapeGrid &other)
	{
		NODE_WIDTH = other.NODE_WIDTH;
		NODE_HEIGHT = other.NODE_HEIGHT;
		tlx = other.tlx;
		tly = other.tly;
		sz = other.sz;
		width = other.width;
		height = other.height;
		data = other.data;
		rawData = new double[height*width*2];
		shapeAreas = new double[height*width];
		for (Index i = 0; i < width*height*2; ++i)
		{
			rawData[i] = other.rawData[i];
			shapeAreas[i/2] = other.shapeAreas[i/2];
		}
		return *this;
	}

	pair<vector<pair<int,int>>,double> find_within( double &x,  double &y,  double &r)
	{
		unordered_set<Index> ret;
		Index cx = (Index) round((x-tlx)/NODE_WIDTH);
		Index cy = (Index) round((y-tly)/NODE_HEIGHT);
		Index rx = ceil(r/(NODE_WIDTH))+1;
		Index ry = ceil(r/(NODE_HEIGHT))+1;
		int hypot2 = rx*rx+ry*ry;
		double r2 = r*r;
		// for (Index i = 1; i <= rx; ++i) // Possible indexing issue here?
		// {
		// 	Index ryLow = ceil(sqrt(hypot2 - i*i));
		// 	for (Index j = 1; j <= ryLow;++j) //Improvement by using symmetry possible
		// 	{
		// 		if	((i+1)*(i+1)*NODE_WIDTH*NODE_WIDTH + (j+1)*NODE_HEIGHT*(j+1)*NODE_HEIGHT <= r2)
		// 		{
		// 			if (i+cx >= 0 && i+cx < data.size() && cy+j >= 0 && cy+j < data[0].size())
		// 			{
		// 				ret.insert(data[i+cx][j+cy].node_data.begin(),data[i+cx][j+cy].node_data.end());
		// 			}
		// 			if (cx-i >= 0 && cx-i < data.size() && cy+j >= 0 && cy+j < data[0].size())
		// 			{
		// 				ret.insert(data[cx-i][cy+j].node_data.begin(),data[cx-i][cy+j].node_data.end());
		// 			}
		// 			if (cx+i >= 0 && cx+i < data.size() && cy-j >= 0 && cy-j < data[0].size())
		// 			{
		// 				ret.insert(data[i+cx][cy-j].node_data.begin(),data[i+cx][cy-j].node_data.end());
		// 			}
		// 			if (cx-i >= 0 && cx-i < data.size() && cy-j >= 0 && cy-j < data[0].size())
		// 			{
		// 				ret.insert(data[cx-i][cy-j].node_data.begin(),data[cx-i][cy-j].node_data.end());
		// 			}
		// 		}

		// 	}
		// }
		// for (Index i = 0; i < max(rx,ry); ++i)
		// {
		// 	if (i*NODE_HEIGHT+NODE_HEIGHT <= r2)
		// 	{
		// 		if (cx >= 0 && cx < data.size() && cy+i < data.size() && cy+i >= 0)
		// 		{
		// 			ret.insert(data[cx][cy+i].node_data.begin(), data[cx][cy+i].node_data.end());					
		// 		}
		// 		if (cx >= 0 && cx < data.size() && cy-i < data.size() && cy-i >= 0)
		// 		{
		// 			ret.insert(data[cx][cy-i].node_data.begin(), data[cx][cy-i].node_data.end());					
		// 		}
		// 	}
		// 	else if (i*NODE_HEIGHT <= r2)
		// 	{
		// 		if (cx >= 0 && cx < data.size() && cy+i < data.size() && cy+i >= 0)
		// 		{
		// 			data[cx][cy+i].queryNode(x,y,r2,this,ret);
		// 		}
		// 		if (cx >= 0 && cx < data.size() && cy-i < data.size() && cy-i >= 0)
		// 		{
		// 			data[cx][cy-i].queryNode(x,y,r2,this,ret);
		// 		}
		// 	}
		// 	if (i*NODE_WIDTH+NODE_WIDTH <= r2)
		// 	{
		// 		if (cx+i >= 0 && cx+i < data.size() && cy < data.size() && cy >= 0)
		// 		{
		// 			ret.insert(data[cx+i][cy].node_data.begin(), data[cx+i][cy].node_data.end());
		// 		}
		// 		if (cx-i >= 0 && cx-i < data.size() && cy < data.size() && cy >= 0)
		// 		{
		// 			ret.insert(data[cx-i][cy].node_data.begin(), data[cx-i][cy].node_data.end());					
		// 		}
		// 	}
		// 	else if (i*NODE_WIDTH <= r2)
		// 	{
		// 		if (cx+i >= 0 && cx+i < data.size() && cy < data.size() && cy >= 0)
		// 		{
		// 			data[cx+i][cy].queryNode(x,y,r2,this,ret);
		// 		}
		// 		if (cx-i >= 0 && cx-i < data.size() && cy < data.size() && cy >= 0)
		// 		{
		// 			data[cx-i][cy].queryNode(x,y,r2,this,ret);
		// 		}

		// 	}
		// }
		for (Index i = 0; i <= rx; ++i) // Possible indexing issue here?
		{
			Index ryLow = ceil(sqrt(hypot2 - i*i));
			for (Index j = 0; j <= ryLow;++j) //Improvement by using symmetry possible
			{
				if	(i*NODE_WIDTH*i*NODE_WIDTH + j*NODE_HEIGHT*j*NODE_HEIGHT <= r2)
				{
					if (i+cx >= 0 && i+cx < data.size() && cy+j >= 0 && cy+j < data[0].size())
					{
						data[i+cx][j+cy].queryNode(x,y,r2,this,ret);
					}
					if (cx-i >= 0 && cx-i < data.size() && cy+j >= 0 && cy+j < data[0].size())
					{
						data[cx-i][cy+j].queryNode(x,y,r2,this,ret);
					}
					if (cx+i >= 0 && cx+i < data.size() && cy-j >= 0 && cy-j < data[0].size())
					{
						data[i+cx][cy-j].queryNode(x,y,r2,this,ret);
					}
					if (cx-i >= 0 && cx-i < data.size() && cy-j >= 0 && cy-j < data[0].size())
					{
						data[cx-i][cy-j].queryNode(x,y,r2,this,ret);
					}
				}
			}
		}
		// if (cx >= 0 && cx < data.size() && cy >= 0 && cy <= data.size())
		// {
		// 	data[cx][cy].queryNode(x,y,r2,this,ret);
		// }

		// double r2 = r*r;
		// for (auto i:data)
		// {
		// 	for(auto j:i)
		// 	{
		// 		j.queryNode(x,y,r2,this,ret);
		// 	}
		// }

		vector<pair<int,int>> ret2;
		double ret3 = 0.0;
		double hk[2] {x,y};
		for (auto pt:ret)
		{
			pair<int,int> pos;
			pos = pos_from_pointer(pt);
			ret2.push_back(pos);
			double* corners[4];
			getCorners(pt,corners);
			if (shapeAreas[pt/2] < 0)
			{
				double intersection[2];
				if (getIntersection(corners[0],corners[1],corners[3],corners[2], intersection))
				{
					//Shape goes p1 ->  intersection -> p4 -> p1, p3 -> intersection -> p2 ->p3
					ret3 -= polyCircleOverlap(corners[0],intersection,corners[3],hk,r)/shapeAreas[pt/2];
					ret3 -= polyCircleOverlap(corners[2],intersection,corners[1],hk,r)/shapeAreas[pt/2];
					
				}
				else 
				{
					getIntersection(corners[0],corners[2],corners[1],corners[3],intersection);
					ret3 -= polyCircleOverlap(corners[0],corners[2],intersection,hk,r)/shapeAreas[pt/2];
					ret3 -= polyCircleOverlap(corners[1],intersection,corners[3],hk,r)/shapeAreas[pt/2];
					//goes p1 -> p3 -> intersection -> p1
					//goes p2 -> intersection -> p4 -> p2
				}
			}
			ret3 += polyCircleOverlap(corners[0],corners[1],corners[2],hk,r)/shapeAreas[pt/2];
			ret3 += polyCircleOverlap(corners[2],corners[1],corners[3],hk,r)/shapeAreas[pt/2];	
		}
		return make_pair(ret2,ret3/ret2.size()*(M_PI*r*r));
	}


	bool insert(Index &ind)
	{
		int minX = INT_MAX;
		int minY = INT_MAX;
		int maxX = INT_MIN;
		int maxY = INT_MIN;
		double * corners[4];
		getCorners(ind,corners);
		double* tl = corners[0];
		double* tr = corners[1];
		double* bl = corners[2];
		double* br = corners[3];

		shapeAreas[ind/2] = getAreaofQuad(tl,tr,br,bl);
		
		auto indices = getIndices(tl,tl+1);
		indices.first < minX ? minX = indices.first : minX = minX;
		indices.first > maxX ? maxX = indices.first : maxX = maxX;
		indices.second < minY ? minY = indices.second : minY = minY;
		indices.second > maxY ? maxY = indices.second : maxY = maxY;
		
		indices = getIndices(tr,tr+1);
		indices.first < minX ? minX = indices.first : minX = minX;
		indices.first > maxX ? maxX = indices.first : maxX = maxX;
		indices.second < minY ? minY = indices.second : minY = minY;
		indices.second > maxY ? maxY = indices.second : maxY = maxY;

		indices = getIndices(bl,bl+1);
		indices.first < minX ? minX = indices.first : minX = minX;
		indices.first > maxX ? maxX = indices.first : maxX = maxX;
		indices.second < minY ? minY = indices.second : minY = minY;
		indices.second > maxY ? maxY = indices.second : maxY = maxY;

		indices = getIndices(br,br+1);
		indices.first < minX ? minX = indices.first : minX = minX;
		indices.first > maxX ? maxX = indices.first : maxX = maxX;
		indices.second < minY ? minY = indices.second : minY = minY;
		indices.second > maxY ? maxY = indices.second : maxY = maxY;
		// cout << minY << "," << minX << "\n";

		Index tlInd = tl - rawData;
		for (int i = minX; i <= maxX;++i)
		{
			for (int j = minY; j <= maxY; ++j)
			{
				if (grid_overlap(i,j,tlInd))
				{
					if (i >= 0 && i < data.size() && j >= 0 && j < data.size())
					{
						data[i][j].addData(tlInd);
						++sz;
					}
				}
			}
		}
		return true;
	}


	~ShapeGrid()
	{
		delete[] rawData;
		delete[] shapeAreas;
	} 

	bool clear()
	{
		sz = 0;
		for (size_t i = 0; i < data.size(); ++i)
		{
			for (size_t j = 0; j < data[0].size(); ++j)
			{
				data[i][j].node_data.clear();
			}
		}
		return true;
	}
};
