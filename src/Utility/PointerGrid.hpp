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
	inline static bool within( double &ptx,  double &pty,  double &r2,  Index dats, PointerGrid * prnt)
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
		void queryNode( double& ptx,  double& pty, double &r2, PointerGrid* prnt, vector<Index> & ret) 
		{
			for (Index i = 0; i < node_data.size(); ++i)
			{
				if (within(ptx,pty,r2,node_data[i],prnt))
				{
					ret.push_back(node_data[i]);						
				}
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
	unordered_map<int,unordered_map<int,Node>> data;

public:
	PointerGrid(double* xx,double* yy, int h, int w, int ndim, int node_count)
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

	pair<vector<pair<int,int>>,double> find_within( double &x,  double &y,  double &r)
	{
		double r2 = r*r;
		int cx = round((x-tlx)/NODE_WIDTH);
		int cy = round((y-tly)/NODE_HEIGHT);
		int rx = ceil(r/(NODE_WIDTH))+1;
		int ry = ceil(r/(NODE_HEIGHT))+1;
		int hypot2 = rx*rx+ry*ry;
		vector<Index> ret;

		if (data.find(cx) != data.end() && data[cx].find(cy) != data[cx].end())  {
			data[cx][cy].queryNode(x,y,r2,this,ret);
		}
		for (int i=1; i <= rx; i++) {
			if (data.find(cx+i) != data.end() && data[cx+i].find(cy) != data[cx+i].end())  {
				data[cx+i][cy].queryNode(x,y,r2,this,ret);
			}
			if (data.find(cx-i) != data.end() && data[cx-i].find(cy) != data[cx-i].end())  {
				data[cx-i][cy].queryNode(x,y,r2,this,ret);
			}
		}
		for (int i=1; i <= ry; i++) {
			if (data.find(cx) != data.end() && data[cx].find(cy+i) != data[cx].end())  {
				data[cx][cy+i].queryNode(x,y,r2,this,ret);
			}
			if (data.find(cx) != data.end() && data[cx].find(cy-i) != data[cx].end())  {
				data[cx][cy-i].queryNode(x,y,r2,this,ret);
			}
		}
		for (int i = 1; i <= rx; ++i) // Possible indexing issue here?
		{
			int ryLow = ceil(sqrt(hypot2 - i*i))+1;
			for (int j = 1; j <= ryLow;++j) //Improvement by using symmetry possible
			{
				// if ((i*NODE_WIDTH)*(i*NODE_WIDTH)+(j*NODE_HEIGHT)*(j*NODE_HEIGHT) <= r2)
				// {
					if ((i+2)*NODE_WIDTH*(i+2)*NODE_WIDTH + (j+2)*NODE_HEIGHT*(j+2)*NODE_HEIGHT < r2) {
						if (data.find(i+cx) != data.end() && data[i+cx].find(cy+j) != data[i+cx].end())  {
							auto &node = data[i+cx][j+cy];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
						if (data.find(cx-i) != data.end() && data[cx-i].find(cy+j) != data[cx-i].end()) {
							auto &node = data[cx-i][cy+j];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
							if (data.find(cx+i) != data.end() && data[cx+i].find(cy-j) != data[cx+i].end()) {
							auto &node = data[i+cx][cy-j];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
							if (data.find(cx-i) != data.end() && data[cx-i].find(cy-j) != data[cx-i].end()) {
							auto &node = data[cx-i][cy-j];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
					}
					else {
						if (data.find(i+cx) != data.end() && data[i+cx].find(cy+j) != data[i+cx].end()) {
							data[i+cx][j+cy].queryNode(x,y,r2,this,ret);
						}
						if (data.find(cx-i) != data.end() && data[cx-i].find(cy+j) != data[cx-i].end()) {
							data[cx-i][cy+j].queryNode(x,y,r2,this,ret);
						}
							if (data.find(cx+i) != data.end() && data[cx+i].find(cy-j) != data[cx+i].end()) {
							data[i+cx][cy-j].queryNode(x,y,r2,this,ret);
						}
							if (data.find(cx-i) != data.end() && data[cx-i].find(cy-j) != data[cx-i].end()) {
							data[cx-i][cy-j].queryNode(x,y,r2,this,ret);
						}
					}
				}
			// }
		}

		// for (auto i:data)
		// {
		// 	for (auto j:i.second)
		// 	{
		// 		j.second.queryNode(x,y,r2,this,ret);
		// 	}
		// }
		vector<pair<int,int>> ret2;
		for (size_t i = 0; i < ret.size(); ++i)
		{
			pair<int,int> pos;
			pos = pos_from_index(ret[i]);
			ret2.push_back(pos);
		}
		double ret3 = ret2.size();
		return make_pair(ret2,ret3);
	}

	bool insert( double* x)
	{
		double * yy = x + 1;
		auto indices = getIndices(x,yy);
		Index i = get<0>(indices);
		Index j = get<1>(indices);
		data[i][j].addData(x-rawData);
		++sz;
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
