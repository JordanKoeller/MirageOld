#include <vector>
#include <cmath>

#define MAX_OBJECTS 8

template <typename V>
class SpatialTree
{
private:
	struct Tree_Datum {
		double x;
		double y;
		V data;
		Tree_Datum() {}
		Tree_Datum(double xx, double yy, V dats):x{xx},y{yy},data{dats} {}
	};
	class Tree_Node
	{
		double cx;
		double cy;
		double sx;
		double sy;
		std::vector<Tree_Datum*> objects;
		std::vector<Tree_Node*> children;
	public:

		friend class SpatialTree<V>;
		Tree_Node() {}
		Tree_Node(double cxx, double cyy, double sxx, double syy)
			:cx{cxx},cy{cyy},sx{sxx},sy{syy}
			{
				objects.resize(MAX_OBJECTS);
				children.resize(4);
			}

		int whichChild(Tree_Datum *obj)
		{
			return (obj->x > cx ? 1 : 0) + (obj->y > cy ? 2 : 0);
		}

		void makeChildren()
		{
			Tree_Node *tmp {new Tree_Node(cx - sx / 4, cy - sy / 4, sx / 2, sy / 2)};
			children.push_back(tmp);
			tmp = new Tree_Node(cx + sx / 4, cy - sy / 4, sx / 2, sy / 2);
			children.push_back(tmp);
			tmp = new Tree_Node(cx - sx / 4, cy + sy / 4, sx / 2, sy / 2);
			children.push_back(tmp);
			tmp = new Tree_Node(cx + sx / 4, cy + sy / 4, sx / 2, sy / 2);
			children.push_back(tmp);
		}

		bool overlap(double objx, double objy, double radius)
		{
			return objx - radius < cx + sx / 2 &&
				objx + radius > cx - sx / 2 &&
				objy - radius < cy + sy / 2 &&
				objy + radius > cy - sy / 2;
		}

	};

	int sz;
	Tree_Node *root;
	double xmin;
	double xmax;
	double ymin;
	double ymax;

	double distance(double ax,double ay,double bx,double by)
	{
		double dx = bx - ax;
		double dy = by - ay;
		return sqrt(dx*dx + dy*dy);
	}
	void searchRecur(double &objx, double &objy, double &radius, Tree_Node *n, std::vector<V> &ret)
	{
		if (n->children.empty())
		{
			for (auto obj:n->objects)
			{
				if (distance(obj->x,obj->y,objx,objy) < radius)
				{
					ret.push_back(obj->data);
				}
			}
		}
		else
		{
			for (auto child:n->children)
			{
				if (child->overlap(objx, objy, radius))
				{
					searchRecur(objx, objy, radius, child, ret);
				}
			}
		}
	}

	void addRecur(Tree_Datum *data, Tree_Node *n)
	{
		if (n->children.empty())
		{
			if (n->objects.size() < MAX_OBJECTS)
			{
				n->objects.push_back(data);
				return;
			}
			else
			{
				n->makeChildren();
				for (auto o:n->objects)
				{
					addRecur(o, n->children[n->whichChild(o)]);
				}
				n->objects.clear();
				addRecur(data, n->children[n->whichChild(data)]);
			}
		}
		else
		{
			addRecur(data, n->children[n->whichChild(data)]);
		}
	}

public:

	SpatialTree():sz{0},xmin{-1.0},xmax{1.0},ymin{-1.0},ymax{1.0} {
		root = new Tree_Node((xmax + xmin) / 2, (ymax + ymin) / 2, xmax - xmin, ymax - ymin);
	}

	bool add(V &data, double posx, double posy)
	{
		if (!(posx > xmin && posx < xmax && posy > ymin && posy < ymax))
		{
			return false;
		}
		else
		{
			Tree_Datum *tmp {new Tree_Datum(posx, posy, data)};
			addRecur(tmp, root);
			sz++;
			return true;
		}
	}

	std::vector<V> findAround(double objx, double objy, double radius)
	{
		std::vector<V> ret;
		searchRecur(objx, objy, radius, root, ret);
		return ret;
	}
};