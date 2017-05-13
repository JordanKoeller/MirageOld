#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>

using namespace std;


class Pixel
{
public:
	double x;
	double y;
	int pixelX;
	int pixelY;
	Pixel() {}
	Pixel(const double dx, const double dy, const int px, const int py):x{dx},y{dy},pixelX{px},pixelY{py} {}
};


class Grid
{
private:

	inline static double hypot(const double& x1, const double& y1, const double& x2, const double& y2) 
	{
		double dx = x2 - x1;
		double dy = y2-y1;
		return sqrt(dx*dx+dy*dy);
	}

	inline static bool within(const double &ptx, const double &pty, const double &radius, const Pixel& data)
	{
		if (hypot(ptx,pty,data.x,data.y) <= radius)
		{
			return true;
		}
		else {
			return false;
		}
	}

	inline bool overlap(const double &objx, const double& objy, const double &radius, const int &i, const int &j) const
	{
		double tnx = tlx + i*NODE_WIDTH;
		double tny = tly + j*NODE_HEIGHT;
		double bnx = tlx + (i+1)*NODE_WIDTH;
		double bny = tly + (j+1)*NODE_HEIGHT;
		return objx - radius <= bnx && objx + radius > tnx && objy - radius <= bny && objy + radius > tny; //BIG possible bug spot.
	}

	inline pair<double,double> getIndices(const double &x,const double &y)
	{
		double xx  = (x - tlx)/NODE_WIDTH;
		double yy  = (y - tly)/NODE_HEIGHT;
		//cout << "xx = " << lrint(xx+0.5) << " , yy = " << lrint(0.5+yy) << "\n";
		// //cout << "for x = " << x << ", y = " << y << endl;
		return make_pair(xx,yy);				
	}

	class Node
	{
	private:
	public:
		std::vector<Pixel> node_data;
		void addData(const double& x, const double& y, const int& px, const int& py)
		{
			auto putting = Pixel(x,y,px,py);
			node_data.push_back(putting);
		}
		std::vector<Pixel> queryNode(const double& ptx, const double& pty,const double &radius) const
		{
			std::vector<Pixel> ret;
			for (size_t i = 0; i < node_data.size(); ++i)
			{
				if (within(ptx,pty,radius,node_data[i]))
				{
					ret.push_back(node_data[i]);						
				}
			}
			return ret;
		}

		void printNode() const
		{
			//cout << " | ";
			for (size_t i = 0; i < node_data.size(); ++i)
			{
				//cout << node_data[i].x << "," << node_data[i].y << " ; ";
			}
			//cout << "|";
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
	std::vector<std::vector<Node>> data;
public:

	/* ------------------------------------------
	   ------ Debugging methods -----------------
	   ------------------------------------------
	*/
	void debug() const
	{
		//cout << "Node width = " << NODE_WIDTH << endl;
		//cout << "tlx = " << tlx << endl;
		//cout << "tly = " << tly << endl;
	}

	void printGrid() const
	{
		for (auto i:data)
		{
			int counter = 0;
			for (auto j:i) 
			{
				//cout << "<" << counter++ << ">";
				j.printNode();
			}
			//cout <<"\n";
		}
	}

	Grid(const double &top_left_x, const double& top_left_y, const double& bottom_right_x,const double& bottom_right_y, const int &node_count)
	{
		constructGrid(top_left_x, top_left_y, bottom_right_x,bottom_right_y,node_count);
		sz = 0;
	}

	void constructGrid(const double& x1, const double& y1, const double& x2, const double& y2, const int &node_count)
	{
		tlx = x1;
		tly = y1;
		int rootNodes = (int) sqrt(node_count);
		// cout << "Number of nodes = " << rootNodes << "\n";
		data = std::vector<std::vector<Node>>(rootNodes+1,std::vector<Node>(rootNodes+1));
		NODE_HEIGHT = (y2 - y1)/ (float) rootNodes;
		NODE_WIDTH = (x2 - x1)/(float) rootNodes;
		NODE_HEIGHT > NODE_WIDTH ? LARGE_AXIS = NODE_HEIGHT : LARGE_AXIS = NODE_WIDTH;

	}

	Grid(const vector<pair<pair<double,double>,pair<int,int>>>::iterator i1, const vector<pair<pair<double,double>,pair<int,int>>>::iterator i2, const int &node_count)
	{
		double minX = 1e30;
		double minY = 1e30;
		double maxX = -1e30;
		double maxY = -1e30;
		sz = 0;
		for (auto i=i1; i != i2; i++)
		{
			pair<pair<double,double>,pair<int,int>> &t = *i;
			get<0>(get<0>(t)) > maxX ? maxX = get<0>(get<0>(t)) : maxX = maxX;
			get<0>(get<0>(t)) < minX ? minX = get<0>(get<0>(t)) : minX = minX;
			get<1>(get<0>(t)) > maxY ? maxY = get<1>(get<0>(t)) : maxY = maxY;
			get<1>(get<0>(t)) < minY ? minY = get<1>(get<0>(t)) : minY = minY;
		}
		constructGrid(minX,minY,maxX,maxY,node_count);		
		for (auto i=i1; i != i2; i++) {
			pair<pair<double,double>,pair<int,int>> &t = *i;
			insert(get<0>(get<0>(t)),get<1>(get<0>(t)),get<0>(get<1>(t)),get<1>(get<1>(t)));
		}
	}
	Grid()=default;

	vector<Pixel> find_within(const double &x, const double &y, const double &r) const
	{
		double cx = (x-tlx)/NODE_WIDTH;
		double cy = (y-tly)/NODE_HEIGHT;
		double rx = r/(NODE_WIDTH) + 1;
		double ry = r/(NODE_HEIGHT) + 1;
		// cout << "Center at " << cx << "," << cy << " with radius^2 " << rr << endl;
		vector<Pixel> ret;

		// #pragma omp parallel for
		for (int i = cx - rx; i <= cx + rx; ++i) // Possible indexing issue here?
		{
			for (int j = cy - ry; j <= cy + ry;++j) //Improvement by using symmetry possible
			{
				if (i >= 0 && j >= 0 && i < data.size() && j < data[0].size())
				{
					vector<Pixel> tmp = data[i][j].queryNode(x,y,r);
					for (auto elem:tmp)
					{
						ret.push_back(elem);
					}
				}
			}
		}
		return ret;
	}

	bool insert(const double& x, const double& y, const int& px, const int &py)
	{
		auto indices = getIndices(x,y);
		// //cout << "Pixel = " << d.x << "," << d.y << endl;
		if (get<0>(indices) >= 0 && get<1>(indices) >= 0 && get<0>(indices) < data.size() && get<1>(indices) < data[0].size())
		{
			data[lrint(get<0>(indices))][lrint(get<1>(indices))].addData(x,y,px,py);
			++sz;
			return true;
		}
		return false;
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