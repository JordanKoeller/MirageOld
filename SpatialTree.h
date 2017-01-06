#include <vector>
#include <cmath>
#include <iostream>

// #define MAXOBJS 8
using std::vector;
class Pixel
{
public:
	int x;
	int y;
	Pixel() {}
	Pixel(int dx, int dy):x{dx},y{dy} {}
};
class SpatialTree {
private:
	static const int MAXOBJS = 128;
	int sz;
	int cntr;
	double xmin;
	double xmax;
	double ymin;
	double ymax;
	struct Datum
	{
		double x;
		double y;
		Pixel data;
		Datum() {}
		Datum(double a, double b, Pixel c):x{a},y{b},data{c} {}
	};
	struct Node
	{
		bool isLeaf;
		int size;
		double cx;
		double cy;
		double sx;
		double sy;
		vector<Datum> objects;
		vector<Node> children;
		Node():isLeaf{true},size{0} {
			// objects.resize(MAXOBJS);
			// children.resize(4);
		}
		Node(double cxx, double cyy, double sxx, double syy):isLeaf{true},size{0},cx{cxx},cy{cyy},sx{sxx},sy{syy} {
			// objects.resize(MAXOBJS);
			// children.resize(4);
		}
	};


	Node *root; 

	double distance(const double &ax, const double &ay, const double &bx, const double &by) const
	{
		double dx = ax-bx;
		double dy = ay-by;
		return sqrt(dx*dx+dy*dy);
	}

	int whichChild(const Datum &obj, const Node *node) const 
	{
		return (obj.x > node->cx ? 1 : 0) + (obj.y > node->cy ? 2 : 0);
	}

	void makeChildren(Node *node)
	{
		// std::cout << "Making children \n";
		// std::cout << node << "\n";
		Node tmp {Node(node->cx-node->sx/4,node->cy-node->sy/4,node->sx/2,node->sy/2)};
		node->children.push_back(tmp);
		tmp = Node(node->cx+node->sx/4,node->cy-node->sy/4,node->sx/2,node->sy/2);
		node->children.push_back(tmp);
		tmp = Node(node->cx-node->sx/4,node->cy+node->sy/4,node->sx/2,node->sy/2);
		node->children.push_back(tmp);
		tmp = Node(node->cx+node->sx/4,node->cy+node->sy/4,node->sx/2,node->sy/2);
		node->children.push_back(tmp);
		node->isLeaf = false;
		return;
	}

	bool overlap(double &objx, double &objy, double &radius, Node *node)
	{
		return objx - radius < node->cx + node->sx / 2 && objx + radius > node->cx - node->sx / 2 &&
			objy - radius < node->cy + node->sy / 2 && objy + radius > node->cy - node->sy / 2;
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


	void searchRecur(double &objx,double &objy,double &radius, Node *n,std::vector<Pixel> &ret)
	{
		if (n->isLeaf)
		{
			for (auto i:n->objects)
			{
				if (distance(i.x,i.y,objx,objy) < radius)
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
			if (node->objects.empty())
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
			return 1;
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
		root = new Node((xmx+xmn)/2,(ymx+ymn)/2,xmx-xmn,ymx-ymn);
		}
	SpatialTree() {
		sz = 0;
		cntr = 0;
		xmin = -1e7;
		xmax = 1e7;
		ymin = -1e7;
		ymax = 1e7;
		// std::cout << "About to make root \n";
		root = new Node((xmax+xmin)/2,(ymax+ymin)/2,xmax-xmin,ymax-ymin);
	}
	~SpatialTree() {
		if (root != nullptr)
		{
			// std::cout << "Delete destructor" << "\n";
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
			Pixel tmp = Pixel(dx,dy);
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

	vector<Pixel> query_point(double ptx, double pty, double radius)
	{
		std::vector<Pixel> ret;
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

};