#include <vector>
#include <cmath>
#include <iostream>

#define MAXOBJS 256

// #define CONTAINS(OX,OY,LX,LY,HX,HY) ((OX)> (LX) && (OX) <= (HX) && (OY) > (LY) && (OY) <= (HY))

using std::vector;
// class Pixel
// {
// public:
// 	int x;
// 	int y;
// 	Pixel() {}
// 	Pixel(int dx, int dy):x{dx},y{dy} {}
// };

template<typename T>
class SpatialTree {
private:
	// static const int MAXOBJS = 8;
	int sz;
	int cntr;
	double xmin;
	double xmax;
	double ymin;
	double ymax;
	// struct Datum
	// {
	// 	double x;
	// 	double y;
	// 	T data;
	// 	Datum() {}
	// 	Datum(double a, double b, T c):x{a},y{b},data{c} {}
	// };
	struct Node
	{
		bool isLeaf;
		bool isDestroyed;
		int size;
		double lx; //low x
		double ly; //low y
		double hx; //high x
		double hy; //high y
		vector<Datum> objects;
		vector<Node> children;
		Node():isLeaf{true},isDestroyed{false},size{0} {
			// objects.resize(MAXOBJS);
			// children.resize(4);
		}
		Node(double lxx, double lyy, double hxx, double hyy):isLeaf{true},isDestroyed{false},size{0},lx{lxx},ly{lyy},hx{hxx},hy{hyy} {
			// objects.resize(MAXOBJS);
			// children.resize(4);
		}
	};


	Node *root; 


	// int whichChild(const Datum &obj, const Node *node) const  //TODO
	// {
	// 	unsigned int cntr = 0;

	// 	for (;cntr < node->children.size();cntr++)
	// 	{
	// 		if (CONTAINS(obj.x,obj.y,node->children[cntr].lx,node->children[cntr].ly,node->children[cntr].hx,node->children[cntr].hy))
	// 		{
	// 			return cntr;
	// 		}
	// 	}
	// 	return 5;
	// }

	int whichChild(const Datum &obj, const Node *node) const 
	{
		double cx = (node->hx+node->lx)/2;
		double cy = (node->hy+node->ly)/2;
		return (obj.x > cx ? 1 : 0) + (obj.y > cy ? 2 : 0);
	}

	void makeChildren(Node *node)
	{
		// std::cout << "Making children \n";
		// std::cout << node << "\n";
		double cx = (node->hx+node->lx)/2;
		double cy = (node->hy+node->ly)/2;
		Node tmp {Node(node->lx,node->ly,cx,cy)};
		node->children.push_back(tmp);
		tmp = Node(cx,node->ly,node->hx,cy);
		node->children.push_back(tmp);
		tmp = Node(node->lx,cy,cx,node->hy);
		node->children.push_back(tmp);
		tmp = Node(cx,cy,node->hx,node->hy);
		node->children.push_back(tmp);
		node->isLeaf = false;
		return;
	}

	bool overlap(double &objx, double &objy, double &radius, Node *node) ////TODO
	{
		return objx - radius < node->hx && objx + radius > node->lx &&
			objy - radius < node->hy && objy + radius > node->ly;
	}

	const bool CONTAINS(const double &objx, const double &objy, const Node *node)
	{
		return objx > node->lx && objx <= node->hx && objy > node->ly && objy <= node->hy;
	}

// #define PART_DISTANCE(AX,AY,BX,BY) (((AX)-(BX))*((AX)-(BX)) + ((AX)-(BX))*((AX)-(BX)))
	double distance(const double &ax, const double &ay, const double &bx, const double &by)
	{
		double dx = ax-bx;
		double dy = ay-by;
		return dx*dx+dy*dy;
	}

	void trimTreeRecur(Node *node)
	{
		if (node->isDestroyed)
		{
			std::cout << "Aww crap \n";
		}
		if (node->isLeaf)
		{
			return;
		}
		else
		{
			for (auto i = node->children.begin();i != node->children.end();i++)
			{
				if ((*i).isLeaf && (*i).objects.size() == 0)
				{
					(*i).isDestroyed = true;
					// i = node->children.erase(i);
				}
				else if (!(*i).isLeaf)
				{
					trimTreeRecur(&(*i));
				}
			}
			if (node->isDestroyed)
			{
				std::cout << "Aww crap \n";
			}
			return;
		}
	}

	void addRecur(Datum &obj, Node *n)
	{
		// std::cout << "Recursing add \n";
		if (n->isLeaf)
		{
			if (n->size < MAXOBJS)
			{
				n->size++;
				n->objects.push_back(obj);
				return;
			}
			else
			{
				makeChildren(n);
				n->size = 0;
				for (auto o:n->objects)
				{
					addRecur(o,&(n->children[whichChild(o, n)]));
				}
				n->objects.clear();
				addRecur(obj,&n->children[whichChild(obj, n)]);
				return;
			}
		}
		else
		{
			addRecur(obj,&n->children[whichChild(obj, n)]);
			return;
		}
	}



	void searchRecur(double &objx,double &objy,double &radius, Node *n,std::vector<T> &ret)
	{
		if (n->isLeaf)
		{
			for (auto i:n->objects)
			{
				if (distance(i.x,i.y,objx,objy) < radius*radius)
				{
					ret.push_back(i.data);
				}
				// std::cout << "Failing to push \n";
			}
		}
		else
		{
			for (auto child:n->children)
			{
				if (overlap(objx,objy,radius,&child))
				{
					searchRecur(objx,objy,radius,&child,ret);
				}
			}
		}
	}


	int numEmpty( Node *node)
	{
		if (node->isLeaf)
		{
			if (node->isDestroyed)
			{
				return 0;
			}
			else if (node->objects.empty())
			{
				return 1;
			}
			else
			{
				return 0;
			}
		}
		else
		{
			int counter = 0;
			for (auto i:node->children)
			{
				counter += numEmpty(&i);
			}
			return counter;
		}
	}

	int countNodes(Node *node)
	{
		if (node->isLeaf)
		{
			if (node->isDestroyed)
			{
				return 0;
			}
			else
			{
				return 1;
			}
		}
		else {
			int counter = 0;
			for (auto i:node->children)
			{
				counter += countNodes(&i);
			}
			return counter;
		}
	}

public:
	SpatialTree(double xmn, double xmx, double ymn, double ymx) {
		sz = 0;
		cntr = 0;
		xmax = xmx;
		xmin = xmn;
		ymax = ymx;
		ymin = ymn;
		root = new Node(xmn,ymn,xmx,ymx);
		}
	SpatialTree() {
		sz = 0;
		cntr = 0;
		xmin = -1e7;
		xmax = 1e7;
		ymin = -1e7;
		ymax = 1e7;
		// std::cout << "About to make root \n";
		root = new Node(xmin,ymin,xmax,ymax);
	}
	~SpatialTree() {
		if (root != nullptr)
		{
			std::cout << "Delete destructor" << "\n";
			delete root;
		}
	}
	SpatialTree(const SpatialTree &that) {
		//TODO
		root = that.root;
		sz = that.sz;
		cntr = that.cntr;
	}
	SpatialTree &operator=(SpatialTree that) {
		root = that.root;
		sz = that.sz;
		cntr = that.cntr;
		return *this;
	}
	bool insert(int dx, int dy, double posx, double posy)
	{
		if (!(posx > xmin && posx < xmax && posy > ymin && posy < ymax))
		{
			return false;
		}
		else
		{
			T tmp = T(dx,dy);
			Datum data = Datum(posx,posy,tmp);
			// std::cout << "Calling insert \n";
			addRecur(data, root);
			sz++;
			return true;
		}
	}
	int size()
	{
		return sz;
	}

	int getEmptyCount()
	{
		return numEmpty(root);
	}

	int getNodeCount()
	{
		return countNodes(root);
	}

	void trimTree()
	{
		trimTreeRecur(root);
		return;
	}

	vector<T> query_point(double ptx, double pty, double radius)
	{
		std::vector<T> ret;
		if (ptx > xmin && ptx < xmax && pty > ymin && pty < ymax)
		{
			searchRecur(ptx,pty,radius,root,ret);
			return ret;
		}
		else
		{
			return ret;
		}
	}

	int query_point_count(double ptx, double pty, double radius)
	{
		std::vector<T> ret;
		if (ptx > xmin && ptx < xmax && pty > ymin && pty < ymax)
		{
			searchRecur(ptx,pty,radius,root,ret);
			return ret.size();
		}
		else
		{
			return ret.size();
		}
	}

};