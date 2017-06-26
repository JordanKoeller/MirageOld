#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>
#include <unordered_map>

using namespace std;


class PointerGrid
{
private:
	typedef  unsigned int Index;
	// friend class PointerGrid::Node;
	double* rawData;


	inline static double hypot2( double& x1,  double& y1,  double& x2,  double& y2)
	{
		double dx = x2 - x1;
		double dy = y2 - y1;
		return dx*dx+dy*dy;
	}
	inline static bool within( double &ptx,  double &pty,  double &r2,  Index &dats, PointerGrid * prnt)
	{
		return hypot2(ptx,pty,*(prnt->rawData+dats),*(prnt->rawData+dats+1)) <= r2;
	}

	inline pair<int,int> pos_from_index(Index &ind)
	{
		int diff = ind/2;
		int y = diff % width;
		int x = diff / width;
		return make_pair(x,y);
	}


	inline pair<Index,Index> getIndices( double *x, double *y)
	{
		Index xx  = round((((*x) - tlx)/NODE_WIDTH));
		Index yy  = round((((*y) - tly)/NODE_HEIGHT));
		return make_pair(xx,yy);				
	}


	void constructGrid( double& x1,  double& y1,  double& x2,  double& y2,  int &node_count)
	{
		tlx = x1;
		tly = y1;
		int rootNodes = (int) sqrt(node_count);
		data = vector<vector<Node>>(rootNodes,vector<Node>(rootNodes));
		NODE_HEIGHT = (y2 - y1)/ (double) rootNodes;
		NODE_WIDTH = (x2 - x1)/(double) rootNodes;

	}
	struct Node
	{
		std::vector<Index> node_data;
		void addData(Index x)
		{
			node_data.push_back(x);
		}
		void queryNode( double& ptx,  double& pty, double &r2, PointerGrid* prnt, vector<pair<int,int>> & ret) 
		{
			for (Index i = 0; i < node_data.size(); ++i)
			{
				if (within(ptx,pty,r2,node_data[i],prnt))
				{
					ret.push_back(prnt->pos_from_index(node_data[i]));						
				}
			}
		}
		void takeAll(PointerGrid* prnt, vector<pair<int,int>> & ret)
		{
			for (auto i:node_data)
			{
				ret.push_back(prnt->pos_from_index(i));						
			}
		}

		Node()=default;
		~Node()=default;

		
	};
	double NODE_WIDTH;
	double NODE_HEIGHT;
	double tlx;
	double tly;
	unsigned int sz;
	int width;
	int height;
	vector<vector<Node>> data;
	// unordered_map<int,unordered_map<int,Node>> data;

public:
	PointerGrid(double* xx,double* yy, int h, int w, int ndim, int node_count)
	{
		width = w;
		height = h;
		double minX = DBL_MAX;
		double minY = DBL_MAX;
		double maxX = DBL_MIN;
		double maxY = DBL_MIN;
		rawData = new double[width*height*2];
		int i = 0;
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				i = (x*w + y);
//				cout << x << " , " << y << " ==> " << i << "\n";
				minX = min(minX,xx[i]);
				minY = min(minY,yy[i]);
				maxX = max(maxX,xx[i]);
				maxY = max(maxY,yy[i]);
				rawData[i*2] = xx[i];
				rawData[i*2+1] = yy[i];
			}
		}
		constructGrid(minX,minY,maxX,maxY,node_count);
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				i = 2*(x*w+y);
				insert(rawData+i);
			}
		}
		cout << "Done constructing\n";
	}

	PointerGrid()
	{
		rawData = new double{10};
	}

	PointerGrid(const PointerGrid &other)
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
		for (int i = 0; i < width*height*2; ++i)
		{
			rawData[i] = other.rawData[i];
		}
	}

	PointerGrid &operator=(const PointerGrid &other)
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
		for (int i = 0; i < width*height*2; ++i)
		{
			rawData[i] = other.rawData[i];
		}
		return *this;
	}

	vector<pair<int,int>> find_within( double &x,  double &y,  double &r)
	{
		double r2 = r*r;
		Index cx = round((x-tlx)/NODE_WIDTH);
		Index cy = round((y-tly)/NODE_HEIGHT);
		Index rx = ceil(r/(NODE_WIDTH));
		Index ry = ceil(r/(NODE_HEIGHT));
		int hypot2 = rx*rx+ry*ry;
		vector<pair<int,int>> ret;

		if (cx >= 0 && cx < data.size() && cy >= 0 &&  cy < data[0].size())  {
			data[cx][cy].queryNode(x,y,r2,this,ret);
		}
		for (Index i=1; i <= rx; i++) {
			if (cx+i >= 0 && cx+i < data.size() && cy >= 0 && cy < data[0].size())  {
				data[cx+i][cy].queryNode(x,y,r2,this,ret);
			}
			if (cx-i >= 0 && cx-i < data.size() && cy >= 0 && cy < data[0].size())  {
				data[cx-i][cy].queryNode(x,y,r2,this,ret);
			}
		}
		for (Index i=1; i <= ry; i++) {
			if (cx >= 0 && cx < data.size() && cy+i >= 0 && cy+i < data[0].size())  {
				data[cx][cy+i].queryNode(x,y,r2,this,ret);
			}
			if (cx >= 0 && cx < data.size() && cy-i >= 0 && cy-i < data[0].size())  {
				data[cx][cy-i].queryNode(x,y,r2,this,ret);
			}
		}
		for (Index i = 1; i <= rx; ++i) // Possible indexing issue here?
		{
			Index ryLow = ceil(sqrt(hypot2 - i*i));
			for (Index j = 1; j <= ryLow;++j) //Improvement by using symmetry possible
			{
				if ((i+1)*NODE_WIDTH*(i+1)*NODE_WIDTH + (j+1)*NODE_HEIGHT*(j+1)*NODE_HEIGHT < r2) {
					if (i+cx >= 0 && i+cx < data.size() && cy+j >= 0 && cy+j < data[0].size())  {
						data[i+cx][j+cy].takeAll(this,ret);
					}
					if (cx-i >= 0 && cx-i < data.size() && cy+j >= 0 && cy+j < data[0].size()) {
						data[cx-i][cy+j].takeAll(this,ret);
					}
					if (cx+i >= 0 && cx+i < data.size() && cy-j >= 0 && cy-j < data[0].size()) {
						data[i+cx][cy-j].takeAll(this,ret);
					}
					if (cx-i >= 0 && cx-i < data.size() && cy-j >= 0 && cy-j < data[0].size()) {
						data[cx-i][cy-j].takeAll(this,ret);
					}
				}
				else
				{
					if (i+cx >= 0 && i+cx < data.size() && cy+j >= 0 && cy+j < data[0].size()) {
						data[i+cx][j+cy].queryNode(x,y,r2,this,ret);
					}
					if (cx-i >= 0 && cx-i < data.size() && cy+j >= 0 && cy+j < data[0].size()) {
						data[cx-i][cy+j].queryNode(x,y,r2,this,ret);
					}
					if (cx+i >= 0 && cx+i < data.size() && cy-j >= 0 && cy-j < data[0].size()) {
						data[i+cx][cy-j].queryNode(x,y,r2,this,ret);
					}
					if (cx-i >= 0 && cx-i < data.size() && cy-j >= 0 && cy-j < data[0].size()) {
						data[cx-i][cy-j].queryNode(x,y,r2,this,ret);
					}
				}
			}
		}

		return ret;
	}

	bool insert( double* x)
	{
		double * yy = x + 1;
		auto indices = getIndices(x,yy);
		Index i = get<0>(indices);
		Index j = get<1>(indices);
		if (i >= 0 && j >= 0 && i < data.size() && j < data[0].size())
		{
			data[i][j].addData(x-rawData);
			++sz;
		}
		return true;
	}


	~PointerGrid()
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
