#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>

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

	// inline bool overlap(const double &objx, const double& objy, const double &radius, const int &i, const int &j) const
	// {
	// 	double tnx = tlx + i*NODE_WIDTH;
	// 	double tny = tly + j*NODE_HEIGHT;
	// 	double bnx = tlx + (i+1)*NODE_WIDTH;
	// 	double bny = tly + (j+1)*NODE_HEIGHT;
	// 	// bool flag1 = 
	// 	return objx - radius <= bnx && objx + radius > tnx && objy - radius <= bny && objy + radius > tny; //BIG possible bug spot.
	// }

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
		double minX = DBL_MAX;
		double minY = DBL_MAX;
		double maxX = DBL_MIN;
		double maxY = DBL_MIN;
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

	vector<Pixel> find_within_brute(const double &x, const double &y, const double &r) const {
		vector<Pixel> ret;
		for (auto i:data) {
			for (auto j:i) {
				vector<Pixel> tmp = j.queryNode(x,y,r);
				ret.insert(ret.end(),tmp.begin(),tmp.end());
			}
		}
		return ret;
	}

	vector<Pixel> find_within(const double &x, const double &y, const double &r) const
	{
		int cx = ceil((x-tlx)/NODE_WIDTH);
		int cy = ceil((y-tly)/NODE_HEIGHT);
		int rx = ceil(r/(NODE_WIDTH));
		int ry = ceil(r/(NODE_HEIGHT));
		// cout << "X,Y = " << rx << "," << ry << "\n";
		int hypot2 = rx*rx+ry*ry;
		vector<Pixel> ret;
		vector<Pixel> tmp = data[cx][cy].queryNode(x,y,r);
		// ret.insert(ret.end\\(),tmp.begn(),tmp.end());
		for (size_t i = 0; i <= rx; ++i) // Possible indexing issue here?
		{
			int ryLow = ceil(sqrt(hypot2 - i*i))+1;
			for (size_t j = 0; j <= ryLow;++j) //Improvement by using symmetry possible
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