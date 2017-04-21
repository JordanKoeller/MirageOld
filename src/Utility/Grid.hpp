#include <vector>
#include <cmath>



template<typename T> //Must have a T.x and T.y method
class Grid
{
private:

	double hypot(const double& x1, const double& y1, const double& x2, const double& y2)
	{
		double dx = x2 - x1;
		double dy = y2-y1;
		return sqrt(dx*dx+dy*dy);
	}

	bool within(const double &ptx, const double &pty, const double &radius, const T& data)
	{
		if (hypot(ptx,pty,data.x,data.y) <= radius)
		{
			return true;
		}
		else {
			return false;
		}
	}

	bool overlap(const double &objx, const double& objy, const double &radius, const int &i, const int &j)
	{
		double tnx = tlx + i*NODE_WIDTH;
		double tny = tly + j*NODE_HEIGHT;
		double bnx = tlx + (i+1)*NODE_WIDTH;
		double bny = tly + (j+1)*NODE_HEIGHT;
		return objx - radius < bnx && objx + radius > tnx && objy - radius < bny && objy + radius > tny; //BIG possible bug spot.
	}

	class Node
	{
	private:
		std::vector<T> node_data;
	public:
		void addData(const T &d)
		{
			node_data.push_back(d);
		}
		std::vector<T> queryNode(const double& ptx, const double& pty,const double &radius)
		{
			std::vector<T> ret;
			for (int i = 0; i < node_data.size(); ++i)
			{
				if (within(ptx,pty,radius,node_data[i]))
				{
					ret.push_back(node_data[i]);						
				}
			}
			return ret;
		}
		Node();
		~Node();
		
	};
	double NODE_WIDTH;
	double NODE_HEIGHT;
	double tlx;
	double tly;
	std::vector<std::vector<Node>> data;
public:
	Grid(const double &top_left_x, const double& top_left_y, const double& bottom_right_x,const double& bottom_right_y, const int &node_count)
	{
		constructGrid(top_left_x, top_left_y, bottom_right_x,bottom_right_y,node_count);
	}

	void constructGrid(const double& x1, const double& y1, const double& x2, const double& y2, const int &node_count)
	{
		tlx = x1;
		tly = y1;
		int rootNodes = (int) sqrt(node_count);
		data = std::vector<std::vector<Node>>(rootNodes,std::vector<Node>(rootNodes));
		NODE_HEIGHT = (y2 - y1)/ (float) rootNodes;
		NODE_WIDTH = (x2 - x1)/(float) rootNodes;

	}

	template<typename IteratorBegin, typename IteratorEnd>
	Grid(IteratorBegin i1, IteratorEnd i2, const int &node_count)
	{
		double minX = 1e30;
		double minY = 1e30;
		double maxX = -1e30;
		double maxY = -1e30;
		for (auto i=i1; i1 != i2; i1++)
		{
			T &t = *i1;
			t.x > maxX ? maxX = t.x : maxX = maxX;
			t.x < minX ? minX = t.x : minX = minX;
			t.y > maxY ? maxY = t.y : maxY = maxY;
			t.y < minY ? minY = t.y : minY = minY;
		}
		constructGrid(minX,minY,maxX,maxY,node_count);		
	}
	Grid()=default;

	std::vector<T> query_Point(const double& x, const double& y, const double& radius)
	{
		std::vector<T> ret;
		for (int i = 0; i < data.size(); ++i)
		{
			for (int j = 0; j < data[i].size(); ++j)
			{
				if (overlap(x,y,radius,i,j))
				{
					auto tmp = data[i][j].queryNode(x,y,radius);
					ret.push_back(tmp); //Wrong method. Need a push_back that jjoins two vectors together
				}
			}
		}
		return ret;
	}

	bool addData(const T& d)
	{
		for (int i = 0; i < data.size(); ++i)
		{
			for (int j = 0; j < data[i].size(); ++j)
			{
				if (overlap(d.x,d.y,0.0,i,j))
				{
					data[i][j].addData(d);
					return true;
				}
			}
		}
		return false;
	}

	~Grid();
};