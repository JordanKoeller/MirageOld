#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>
#include <unordered_map>

using namespace std;


class Grid
{
private:

	double* rawData;

	inline static double hypot( double& x1,  double& y1,  double& x2,  double& y2) 
	{
		double dx = x2 - x1;
		double dy = y2-y1;
		return sqrt(dx*dx+dy*dy);
	}
	inline static bool within( double &ptx,  double &pty,  double &radius,  double *data)
	{
		if (hypot(ptx,pty,*data,*(data+1)) <= radius)
		{
			return true;
		}
		else {
			return false;
		}
	}

	// static bool withinQuad( pair<double,double> &p, vector<pair<double,double>> &corners)
	// {
	// 	unsigned int crossings = 0;
	// 	for (int c = 0; c < corners.size(); ++c)
	// 	{
	// 		auto &c1 = corners[c];
	// 		auto &c2 = corners[c%corners.size()];
	// 		if (get<0>(c1) >= get<0>(p) || get<0>(c2) >= get<0>(p))
	// 		{
	// 			if ((get<1>(c1) < get<1>(p) && get<1>(c2) > get<1>(c2)) || (get<1>(c1) > get<1>(p) && get<1>(c2) < get<1>(c2)))
	// 			{
	// 				crossings++;
	// 			}
	// 		}
	// 	}
	// 	if (crossings % 2 == 1)
	// 	{
	// 		return true;
	// 	}
	// 	else
	// 	{
	// 		return false;
	// 	}
	// }

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
		int diff = (pos - rawData)/2;
		int y = diff % width;
		int x = diff / height;
		return make_pair(x,y);
	}

	inline pair<double,double> getIndices( double *x, double *y)
	{
		double xx  = (*x - tlx)/NODE_WIDTH;
		double yy  = (*y - tly)/NODE_HEIGHT;
		return make_pair(xx,yy);				
	}


	void ructGrid( double& x1,  double& y1,  double& x2,  double& y2,  int &node_count)
	{
		tlx = x1;
		tly = y1;
		int rootNodes = (int) sqrt(node_count);
		data = std::unordered_map<int,std::unordered_map<int,Node>>();
		NODE_HEIGHT = (y2 - y1)/ (float) rootNodes;
		NODE_WIDTH = (x2 - x1)/(float) rootNodes;
		NODE_HEIGHT > NODE_WIDTH ? LARGE_AXIS = NODE_HEIGHT : LARGE_AXIS = NODE_WIDTH;

	}
	class Node
	{
	private:
	public:
		std::vector<double*> node_data;
		void addData(double* x)
		{
			node_data.push_back(x);
		}
		std::vector<double*> queryNode( double& ptx,  double& pty, double &radius) 
		{
			std::vector<double*> ret;
			for (size_t i = 0; i < node_data.size(); ++i)
			{
				if (within(ptx,pty,radius,node_data[i]))
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
	double LARGE_AXIS;
	double tlx;
	double tly;
	unsigned int sz;
	int width;
	int height;
	std::unordered_map<int,std::unordered_map<int,Node>> data;

public:
	Grid(double* data, int h, int w, int ndim, int node_count)
	{
		width = w;
		height = h;
		double minX = DBL_MAX;
		double minY = DBL_MAX;
		double maxX = DBL_MIN;
		double maxY = DBL_MIN;
		int i = 0;
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				i = 2*(x*w + y);
				minX = min(minX,data[i]);
				minY = min(minY,data[i+1]);
				maxX = max(maxX,data[i]);
				maxY = max(maxY,data[i+1]);
			}
		}
		ructGrid(minX,minY,maxX,maxY,node_count);
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				i = 2*(x*w+y);
				// cout << "Index of " << i << "\n";
				insert(&data[i],&data[i+1]);
			}
		}
	}

	Grid()=default;

	vector<pair<int,int>> find_within( double &x,  double &y,  double &r)
	{
		int cx = ceil((x-tlx)/NODE_WIDTH);
		int cy = ceil((y-tly)/NODE_HEIGHT);
		int rx = ceil(r/(NODE_WIDTH));
		int ry = ceil(r/(NODE_HEIGHT));
		int hypot2 = rx*rx+ry*ry;
		vector<double*> ret;
		vector<double*> tmp = data[cx][cy].queryNode(x,y,r);
		ret.insert(ret.end(),tmp.begin(),tmp.end());
		for (size_t i=1; i <= rx; i++) {
				tmp = data[cx+i][cy].queryNode(x,y,r);
				ret.insert(ret.end(),tmp.begin(),tmp.end());
				tmp = data[cx-i][cy].queryNode(x,y,r);
				ret.insert(ret.end(),tmp.begin(),tmp.end());
		}
		for (size_t i=1; i <= ry; i++) {
				tmp = data[cx][cy+i].queryNode(x,y,r);
				ret.insert(ret.end(),tmp.begin(),tmp.end());
				tmp = data[cx][cy-i].queryNode(x,y,r);
				ret.insert(ret.end(),tmp.begin(),tmp.end());
		}
		for (size_t i = 1; i <= rx; ++i) // Possible indexing issue here?
		{
			int ryLow = ceil(sqrt(hypot2 - i*i))+1;
			for (size_t j = 1; j <= ryLow;++j) //Improvement by using symmetry possible
			{
				if ((i*NODE_WIDTH)*(i*NODE_WIDTH)+(j*NODE_HEIGHT)*(j*NODE_HEIGHT) <= r)
				{
					if ((i+2)*NODE_WIDTH*(i+2)*NODE_WIDTH + (j+2)*NODE_HEIGHT*(j+2)*NODE_HEIGHT < r*r) {
						if (i+cx >= 0 && i+cx < data.size() && j+cy >= 0 && j+cy < data[0].size()) {
							auto &node = data[i+cx][j+cy];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
						if (cx-i >= 0 && cx-i < data.size() && j+cy >= 0 && j+cy < data[0].size()) {	
							auto &node = data[cx-i][cy+j];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
							if (cx+i >= 0 && cx+i < data.size() && cy-j >= 0 && cy-j< data[0].size()) {	
							auto &node = data[i+cx][cy-j];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}
							if (cx-i >= 0 && cx-i < data.size() && cy-j >= 0 && cy-j< data[0].size()) {	
							auto &node = data[cx-i][cy-j];
							ret.insert(ret.end(),node.node_data.begin(), node.node_data.end());
						}						
					}
					else {
						if (i+cx >= 0 && i+cx < data.size() && j+cy >= 0 && j+cy < data[0].size()) {
							tmp = data[i+cx][j+cy].queryNode(x,y,r);
							ret.insert(ret.end(),tmp.begin(),tmp.end());
						}
						if (cx-i >= 0 && cx-i < data.size() && j+cy >= 0 && j+cy < data[0].size()) {	
							tmp = data[cx-i][cy+j].queryNode(x,y,r);
							ret.insert(ret.end(),tmp.begin(),tmp.end());
						}
							if (cx+i >= 0 && cx+i < data.size() && cy-j >= 0 && cy-j< data[0].size()) {	
							tmp = data[i+cx][cy-j].queryNode(x,y,r);
							ret.insert(ret.end(),tmp.begin(),tmp.end());
						}
							if (cx-i >= 0 && cx-i < data.size() && cy-j >= 0 && cy-j< data[0].size()) {	
							tmp = data[cx-i][cy-j].queryNode(x,y,r);
							ret.insert(ret.end(),tmp.begin(),tmp.end());
						}
					}
				}
			}
		}
		vector<pair<int,int>> ret2;
		for (int i = 0; i < ret.size(); ++i)
		{
			pair<int,int> pos;
			pos = pos_from_pointer(ret[i]);
			ret2.push_back(pos);
		}
		return ret2;
	}

	bool insert( double* x, double* y)
	{
		auto indices = getIndices(x,y);
		int i = lrint(get<0>(indices));
		int j = lrint(get<1>(indices));
		data[i][j].addData(x);
		++sz;
		return true;
	}



	void printBucketSizes()
	{
		vector<size_t> ret;
		for (auto i:data)
		{
			for (auto j:get<1>(i))
			{
				ret.push_back(get<1>(j).node_data.size());
			}
		}
		for (auto i:ret)
		{
			cout << i << "\n";
		}
	}


	~Grid()=default;

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
