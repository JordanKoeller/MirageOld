#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>
#include <unordered_map>
#include <unordered_set>
using namespace std;


class ShapeGrid
{
private:
	class Datum
	{
	public:
		double *tl;
		double *tr;
		double *bl;
		double *br;
		Datum()=default;
		Datum(double *& topleft, double *& topright, double *& bottomleft, double *& bottomright)
		{
			tl = topleft;
			tr = topright;
			bl = bottomleft;
			br = bottomright;
		}
		~Datum()=default;
	};

	double* rawData;

	inline static double hypot( double& x1,  double& y1,  double& x2,  double& y2) 
	{
		double dx = x2 - x1;
		double dy = y2-y1;
		return sqrt(dx*dx+dy*dy);
	}

	inline static double hypot2( double& x1,  double& y1,  double& x2,  double& y2)
	{
		double dx = x2 - x1;
		double dy = y2-y1;
		return dx*dx+dy*dy;
	}
	inline static bool within( double &ptx,  double &pty,  double &radius,  double *dats)
	{
		if (hypot2(ptx,pty,*dats,*(dats+1)) <= radius*radius)
		{
			return true;
		}
		else {
			return false;
		}
	}

	inline bool overlap( double &objx,  double& objy,  double &radius,  int &i,  int &j) 
	{
		double tnx = tlx + i*NODE_WIDTH;
		double tny = tly + j*NODE_HEIGHT;
		double bnx = tlx + (i+1)*NODE_WIDTH;
		double bny = tly + (j+1)*NODE_HEIGHT;
		// bool flag1 = 
		return objx - radius <= bnx && objx + radius > tnx && objy - radius <= bny && objy + radius > tny; //BIG possible bug spot.
	}

	inline pair<int,int> pos_from_pointer(double* pos)
	{
//		cout << pos-rawData << "\n";
		int diff = (pos-rawData)/2;
		int y = diff % width;
		int x = diff / width;
		return make_pair(x,y);
	}

	inline pair<double,double> getIndices( double *x, double *y)
	{
		double xx  = ((*x) - tlx)/NODE_WIDTH;
		double yy  = ((*y) - tly)/NODE_HEIGHT;
		return make_pair(xx,yy);				
	}

	int contigIndex(int i, int j)
	{
		return 2*(i*width+j);
	}

	inline static double project(double* vStart, double*vEnd, double &cx, double &cy)
	{
		//Calculates distance from the line connecting vStart and vEnd to (cx,cy). Done by projecting vector to cx onto the line.
		double C[2];
		double A[2];
		A[0] = vEnd[0]-vStart[0];
		A[1] = vEnd[1]-vStart[1];
		C[0] = cx-vStart[0];
		C[1] = cy-vStart[1];
		double dot = (C[0])*(A[0])+(C[1])*(A[1]);
		double ret =  (C[0])*(C[0])+(C[1])*(C[1])-(dot*dot/((A[0])*(A[0])+(A[1])*(A[1])));
		return ret;
	}

	inline static bool intersect(Datum &datum, double &x, double &y, double &r)
	{
		double r2 = r*r;
		//Check if a corner is within the circle
		if (hypot2(datum.tl[0],datum.tl[1],x,y) <= r2 ||
			hypot2(datum.tr[0],datum.tr[1],x,y) <= r2 ||
			hypot2(datum.bl[0],datum.bl[1],x,y) <= r2 ||
			hypot2(datum.br[0],datum.br[1],x,y) <= r2)
		{
			return true;
		}
		// return false;

		//Check if circle is within the polygon using the Winding Number Algorithm
		int wn = 0;
		double* V [5];
		V[0] = datum.tl;
		V[1] = datum.tr;
		V[2] = datum.br;
		V[3] = datum.bl;
		V[4] = datum.tl;
		double P[2];
		P[0] = x;
		P[1] = y;
		for (int i=0;i < 4;i++)
		{
			// cout << V[i][0] << "," << V[i][1] << "\n";
			if (V[i][1] <= y)
			{
				if (V[i+1][1] > y)
				{
					if (isLeft(V[i],V[i+1],P) > 0)
					{
						wn++;
					}
				}
			}
			else
			{
				if (V[i+1][1] <= y)
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
			cout << "wound\n";
			return true;
		}
		// cout << "\n\n";

		// Check if circle intersects an edge of the shape
		if (abs(project(datum.tr,datum.tl,x,y)) <= r2 ||
			abs(project(datum.br,datum.tr,x,y)) <= r2 ||
			abs(project(datum.bl,datum.br,x,y)) <= r2 ||
			abs(project(datum.tl,datum.bl,x,y)) <= r2)
		{
			return true;
		}
		return false;
	}

	inline static int isLeft(double* p0, double* p1, double* p2)
	{
//    Input:  three points P0, P1, and P2
//    Return: >0 for P2 left of the line through P0 to P1
//          =0 for P2 on the line
//          <0 for P2 right of the line
		return ((p1[0] - p0[0])*(p2[1]-p0[1])-(p2[0]-p0[0])*(p1[1]-p0[1]));
	}



	void constructGrid( double& x1,  double& y1,  double& x2,  double& y2,  int &node_count)
	{
		tlx = x1;
		tly = y1;
		int rootNodes = (int) sqrt(node_count);
		NODE_HEIGHT = (y2 - y1)/ (double) rootNodes;
		NODE_WIDTH = (x2 - x1)/(double) rootNodes;
		NODE_HEIGHT > NODE_WIDTH ? LARGE_AXIS = NODE_HEIGHT : LARGE_AXIS = NODE_WIDTH;

	}


	class Node
	{
	private:
	public:
		std::vector<Datum> node_data;
		void addData(double *topleft, double *topright, double* bottomleft, double* bottomright)
		{
			auto tmp = Datum(topleft,topright,bottomleft,bottomright);
			node_data.push_back(tmp);
		}
		std::vector<double*> queryNode( double& ptx,  double& pty, double &radius) 
		{
			std::vector<double*> ret;
			for (size_t i = 0; i < node_data.size(); ++i)
			{
				// if (within(ptx,pty,radius,node_data[i].tl))
				if (intersect(node_data[i],ptx,pty,radius))
				{
					ret.push_back(node_data[i].tl);
				}
			}
			return ret;
		}
		Node()=default;
		~Node()=default;

		
	};
	double NODE_WIDTH;
	double NODE_HEIGHT;
	double LARGE_AXIS;
	double tlx;
	double tly;
	unsigned int sz;
	int width;
	int height;
	unordered_map<int,unordered_map<int,Node>> data;

public:
	ShapeGrid(double* xx,double* yy, int h, int w, int ndim, int node_count)
	{
		width = w;
		height = h;
		rawData = new double[w*h*2];
		double minX = DBL_MAX;
		double minY = DBL_MAX;
		double maxX = DBL_MIN;
		double maxY = DBL_MIN;
		int i = 0;
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
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
		for (int x = 0; x < w-1; ++x)
		{
			for (int y = 0; y < h-1; ++y)
			{
				insert(rawData+contigIndex(x,y),rawData+contigIndex(x+1,y),rawData+contigIndex(x,y+1),rawData+contigIndex(x+1,y+1));
			}
		}
	}

	ShapeGrid()
	{
		rawData = new double{10};
	}

	ShapeGrid(const ShapeGrid &other)
	{
		NODE_WIDTH = other.NODE_WIDTH;
		NODE_HEIGHT = other.NODE_HEIGHT;
		LARGE_AXIS = other.LARGE_AXIS;
		tlx = other.tlx;
		tly = other.tly;
		sz = other.sz;
		width = other.width;
		height = other.height;
		data = other.data;
		delete[] rawData;
		rawData = other.rawData;
	}

	ShapeGrid &operator=(const ShapeGrid &other)
	{
		NODE_WIDTH = other.NODE_WIDTH;
		NODE_HEIGHT = other.NODE_HEIGHT;
		LARGE_AXIS = other.LARGE_AXIS;
		tlx = other.tlx;
		tly = other.tly;
		sz = other.sz;
		width = other.width;
		height = other.height;
		data = other.data;
		delete[] rawData;
		rawData = other.rawData;
	}

	void query_small(double &x, double &y, double &r, vector<double*> &return_buffer)
	{
		int cx = round((x-tlx)/NODE_WIDTH);
		int cy = round((y-tly)/NODE_HEIGHT);
		int rx = ceil(r/(NODE_WIDTH))+1;
		int ry = ceil(r/(NODE_HEIGHT))+1;
		int hypot2 = rx*rx+ry*ry;

		
				
	}

	vector<pair<int,int>> find_within( double &x,  double &y,  double &r)
	{
		int cx = round((x-tlx)/NODE_WIDTH);
		int cy = round((y-tly)/NODE_HEIGHT);
		int rx = ceil(r/(NODE_WIDTH))+1;
		int ry = ceil(r/(NODE_HEIGHT))+1;
		int hypot2 = rx*rx+ry*ry;
		unordered_set<double*> ret;
		// vector<double*> tmp;
		// tmp = data[cx][cy].queryNode(x,y,r);
		// ret.insert(ret.end(),tmp.begin(),tmp.end());
		// for (size_t i=1; i <= rx; i++) {
		// 		tmp = data[cx+i][cy].queryNode(x,y,r);
		// 		ret.insert(ret.end(),tmp.begin(),tmp.end());
		// 		tmp = data[cx-i][cy].queryNode(x,y,r);
		// 		ret.insert(ret.end(),tmp.begin(),tmp.end());
		// }
		// for (size_t i=1; i <= ry; i++) {
		// 		tmp = data[cx][cy+i].queryNode(x,y,r);
		// 		ret.insert(ret.end(),tmp.begin(),tmp.end());
		// 		tmp = data[cx][cy-i].queryNode(x,y,r);
		// 		ret.insert(ret.end(),tmp.begin(),tmp.end());
		// }
		// for (size_t i = 1; i <= rx; ++i) // Possible indexing issue here?
		// {
		// 	int ryLow = ceil(sqrt(hypot2 - i*i))+1;
		// 	for (size_t j = 1; j <= ryLow;++j) //Improvement by using symmetry possible
		// 	{
		// 		if ((i*NODE_WIDTH)*(i*NODE_WIDTH)+(j*NODE_HEIGHT)*(j*NODE_HEIGHT) <= r)
		// 		{
		// 			if ((i+2)*NODE_WIDTH*(i+2)*NODE_WIDTH + (j+2)*NODE_HEIGHT*(j+2)*NODE_HEIGHT < r*r) {
		// 				if (data.find(i+cx) != data.end() && data[i+cx].find(cy+j) != data[i+cx].end())  {
		// 					auto &node = data[i+cx][j+cy];
		// 					for (auto i:node.node_data)
		// 					{
		// 						ret.push_back(i.tl);
		// 					}
		// 				}
		// 				if (data.find(cx-i) != data.end() && data[cx-i].find(cy+j) != data[cx-i].end()) {
		// 					auto &node = data[cx-i][cy+j];
		// 					for (auto i:node.node_data)
		// 					{
		// 						ret.push_back(i.tl);
		// 					}

		// 				}
		// 					if (data.find(cx+i) != data.end() && data[cx+i].find(cy-j) != data[cx+i].end()) {
		// 					auto &node = data[i+cx][cy-j];
		// 					for (auto i:node.node_data)
		// 					{
		// 						ret.push_back(i.tl);
		// 					}
		// 				}
		// 					if (data.find(cx-i) != data.end() && data[cx-i].find(cy-j) != data[cx-i].end()) {
		// 					auto &node = data[cx-i][cy-j];
		// 					for (auto i:node.node_data)
		// 					{
		// 						ret.push_back(i.tl);
		// 					}
		// 				}
		// 			}
		// 			else {
		// 				if (data.find(i+cx) != data.end() && data[i+cx].find(cy+j) != data[i+cx].end()) {
		// 					tmp = data[i+cx][j+cy].queryNode(x,y,r);
		// 					ret.insert(ret.end(),tmp.begin(),tmp.end());
		// 				}
		// 				if (data.find(cx-i) != data.end() && data[cx-i].find(cy+j) != data[cx-i].end()) {
		// 					tmp = data[cx-i][cy+j].queryNode(x,y,r);
		// 					ret.insert(ret.end(),tmp.begin(),tmp.end());
		// 				}
		// 					if (data.find(cx+i) != data.end() && data[cx+i].find(cy-j) != data[cx+i].end()) {
		// 					tmp = data[i+cx][cy-j].queryNode(x,y,r);
		// 					ret.insert(ret.end(),tmp.begin(),tmp.end());
		// 				}
		// 					if (data.find(cx-i) != data.end() && data[cx-i].find(cy-j) != data[cx-i].end()) {
		// 					tmp = data[cx-i][cy-j].queryNode(x,y,r);
		// 					ret.insert(ret.end(),tmp.begin(),tmp.end());
		// 				}
		// 			}
		// 		}
		// 	}
		// }
		for (auto i:data)
		{
			for (auto j:i.second)
			{
				auto tmp = j.second.queryNode(x,y,r);
				ret.insert(tmp.begin(),tmp.end());
			}
		}
		vector<pair<int,int>> ret2;
		for (auto pt:ret)
		{
			pair<int,int> pos;
			pos = pos_from_pointer(pt);
			ret2.push_back(pos);
			
		}
		// for (int i = 0; i < ret.size(); ++i)
		// {
		// }
		return ret2;
	}

	bool insert( double* tl, double *tr, double * bl, double * br)
	{
		// if (*tl > *tr)
		// {
		// 	swap(tl,tr);
		// }
		// if (*bl > *br)
		// {
		// 	swap(bl,br);
		// }
		// if (tl[1] < bl[1])
		// {
		// 	swap(tl,bl);
		// }
		// if (tr[1] < br[1])
		// {
		// 	swap(tr,br);
		// }
		double * yy = tl + 1;
		auto indices = getIndices(tl,yy);
		int i = get<0>(indices);
		int j = get<1>(indices);
		data[i][j].addData(tl,tr,bl,br);
		++sz;
		return true;
	}


	~ShapeGrid()
	{
		cout << "deleted\n";
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
