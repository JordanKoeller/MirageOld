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


class ShapeGrid
{
	class Node;
public:
	typedef unsigned int Index;
	friend class ShapeGrid::Node;

private:
	double* rawData;


	inline static double hypot2( double& x1,  double& y1,  double& x2,  double& y2)
	{
		double dx = x2 - x1;
		double dy = y2-y1;
		return dx*dx+dy*dy;
	}
 

	// inline static bool lineIntersects(double* a1, double* a2, double* b1, double*b2) //Two points each on line A and line B
	// {
	// 	double m_a = (a2[1]-a1[1])/(a2[0]-a1[0]);
	// 	double m_b = (b2[1]-b1[1])/(b2[0]-b1[0]);
	// 	double y_a = a1[1] - m_a*a1[0];
	// 	double y_b = b1[1] - m_b*b1[0];
	// 	double x = (y_b-y_a)/(m_a-m_b);
	// 	if (abs(a2[0]-a1[0]) == abs(x-a1[0]) + abs(x-a2[0]) &&
	// 		abs(b2[0]-b1[0]) == abs(x-b1[0]) + abs(x-b2[0]))
	// 	{
	// 		return true;
	// 	}
	// 	else
	// 	{
	// 		return false;
	// 	}
	// }
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
		ret[2] = rawData + (tl+2*width);
		ret[3] = rawData + (tl+2*(width+1));
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

	inline static double project(double* vStart, double*vEnd, double &cx, double &cy, double &r2)
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

	bool intersect(Index &tl, double &x, double &y, double &r)
	{
		double r2 = r*r;
		double *V[5];
		getCorners(tl,V);
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

		// return false;
		if (project(V[1],V[0],x,y,r2) ||
			project(V[3],V[1],x,y,r2) ||
			project(V[2],V[3],x,y,r2) ||
			project(V[0],V[2],x,y,r2))
		{
			return true;
		}

		//Check if circle is within the polygon using the Winding Number Algorithm
		if (winding_algorithm(V, P))
		{
			return true;
		}

		// Check if circle intersects an edge of the shape
		return false;
	}

	inline static double isLeft(double* p0, double* p1, double* p2)
	{
		return ((p1[0] - p0[0])*(p2[1]-p0[1])-(p2[0]-p0[0])*(p1[1]-p0[1]));
	}

	bool grid_overlap(int &i, int &j, Index &tl)
	{
		// return true;
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

	}

	struct Node
	{
		std::vector<Index> node_data;
		void addData(Index &tl)
		{
			node_data.push_back(tl);
		}
		std::vector<Index> queryNode( double& ptx,  double& pty, double &radius, ShapeGrid * outer) 
		{
			std::vector<Index> ret;
			for (size_t i = 0; i < node_data.size(); ++i)
			{
				if (outer->intersect(node_data[i],ptx,pty,radius))
				{
					ret.push_back(node_data[i]);
				}
			}
			return ret;
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
	unordered_map<int,unordered_map<int,Node>> data;

public:

	ShapeGrid(double* xx,double* yy, int h, int w, int ndim, int node_count)
	{
		width = (Index) w;
		height = (Index) h;
		rawData = new double[w*h*2];
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
		data.reserve(w*h);
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
		rawData = new double[width*height*2];
		delete[] rawData;
		for (Index i = 0; i < width*height*2; ++i)
		{
			rawData[i] = other.rawData[i];
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
		delete[] rawData;
		rawData = new double[width*height*2];
		for (Index i = 0; i < width*height*2; ++i)
		{
			rawData[i] = other.rawData[i];
		}
		return *this;
	}


	pair<vector<pair<int,int>>,double> find_within( double &x,  double &y,  double &r)
	{
		unordered_set<Index> ret;
		int cx = round((x-tlx)/NODE_WIDTH);
		int cy = round((y-tly)/NODE_HEIGHT);
		Index rx = ceil(r/(NODE_WIDTH))+1;
		Index ry = ceil(r/(NODE_HEIGHT))+1;
		int hypot2 = rx*rx+ry*ry;
		vector<Index> tmp;
		tmp = data[cx][cy].queryNode(x,y,r,this);
		ret.insert(tmp.begin(),tmp.end());
		for (Index i=1; i <= rx; i++) {
				tmp = data[cx+i][cy].queryNode(x,y,r,this);
				ret.insert(tmp.begin(),tmp.end());
				tmp = data[cx-i][cy].queryNode(x,y,r,this);
				ret.insert(tmp.begin(),tmp.end());
		}
		for (Index i=1; i <= ry; i++) {
				tmp = data[cx][cy+i].queryNode(x,y,r,this);
				ret.insert(tmp.begin(),tmp.end());
				tmp = data[cx][cy-i].queryNode(x,y,r,this);
				ret.insert(tmp.begin(),tmp.end());
		}
		for (Index i = 1; i <= rx; ++i) // Possible indexing issue here?
		{
			Index ryLow = ceil(sqrt(hypot2 - i*i))+1;
			for (Index j = 1; j <= ryLow;++j) //Improvement by using symmetry possible
			{
				if ((i*NODE_WIDTH)*(i*NODE_WIDTH)+(j*NODE_HEIGHT)*(j*NODE_HEIGHT) <= r*r)
				{
					if ((i+2)*NODE_WIDTH*(i+2)*NODE_WIDTH + (j+2)*NODE_HEIGHT*(j+2)*NODE_HEIGHT < r*r)
					{
						if (data.find(i+cx) != data.end() && data[i+cx].find(cy+j) != data[i+cx].end()) 
						{
							ret.insert(data[i+cx][j+cy].node_data.begin(), data[i+cx][j+cy].node_data.end());
						}
						if (data.find(cx-i) != data.end() && data[cx-i].find(cy+j) != data[cx-i].end())
						{
							ret.insert(data[cx-i][cy+j].node_data.begin(), data[cx-i][cy+j].node_data.end());
						}
						if (data.find(cx+i) != data.end() && data[cx+i].find(cy-j) != data[cx+i].end())
						{
							ret.insert(data[i+cx][cy-j].node_data.begin(), data[i+cx][cy-j].node_data.end());
						}
						if (data.find(cx-i) != data.end() && data[cx-i].find(cy-j) != data[cx-i].end())
						{
							ret.insert(data[cx-i][cy-j].node_data.begin(), data[cx-i][cy-j].node_data.end());
						}
					}
				}
				else {
					if (data.find(i+cx) != data.end() && data[i+cx].find(cy+j) != data[i+cx].end())
					{
						tmp = data[i+cx][j+cy].queryNode(x,y,r,this);
						ret.insert(tmp.begin(),tmp.end());
					}
					if (data.find(cx-i) != data.end() && data[cx-i].find(cy+j) != data[cx-i].end())
					{
						tmp = data[cx-i][cy+j].queryNode(x,y,r,this);
						ret.insert(tmp.begin(),tmp.end());
					}
					if (data.find(cx+i) != data.end() && data[cx+i].find(cy-j) != data[cx+i].end())
					{
						tmp = data[i+cx][cy-j].queryNode(x,y,r,this);
						ret.insert(tmp.begin(),tmp.end());
					}
					if (data.find(cx-i) != data.end() && data[cx-i].find(cy-j) != data[cx-i].end())
					{
						tmp = data[cx-i][cy-j].queryNode(x,y,r,this);
						ret.insert(tmp.begin(),tmp.end());
					}
				}
			}
		}

		vector<pair<int,int>> ret2;
		for (auto pt:ret)
		{
			pair<int,int> pos;
			pos = pos_from_pointer(pt);
			ret2.push_back(pos);
			
		}
		double ret3;
		ret3 = ret2.size();
		return make_pair(ret2,ret3);
	}


	bool insert(Index &ind)
	{
		int minX = INT_MAX;
		int minY = INT_MAX;
		int maxX = INT_MIN;
		int maxY = INT_MIN;
		double * corners[5];
		getCorners(ind,corners);
		double* tl = corners[0];
		double* tr = corners[1];
		double* bl = corners[2];
		double* br = corners[3];
		
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

		Index tlInd = tl - rawData;
		for (int i = minX; i <= maxX;++i)
		{
			for (int j = minY; j <= maxY; ++j)
			{
				if (grid_overlap(i,j,tlInd))
				{
					data[i][j].addData(tlInd);
					++sz;
				}
			}
		}
		return true;
	}


	~ShapeGrid()
	{
		delete[] rawData;
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
