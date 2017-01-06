#include <vector>
#include <cmath>
#include <iostream>
#include <utility>

#define MAXOBJS 64
#define PART_DISTANCE(AX,AY,BX,BY) (((AX)-(BX))*((AX)-(BX)) + ((AX)-(BX))*((AX)-(BX)))
#define CONTAINS(OX,OY,LX,LY,HX,HY) ((OX)> (LX) && (OX) <= (HX) && (OY) > (LY) && (OY) <= (HY))



template<typename V>
class SpatialTree {
private:
	struct Node
	{
	private:
		bool isLeaf;
		int treeSize;

		double cx;
		double cy;

		std::vector<V> data;
		std::vector<Node *> children;

		Node():isLeaf{true},treeSize{0},cx{0.0},cy{0.0} {}

		// Node &operator=(Node &that)
		// {
		// 	isLeaf = that.isLeaf;
		// 	treeSize = that.treeSize;
		// 	cx = that.treeSize;
		// 	cy = that.treeSize;
		// 	data = that.data;
		// 	children = that.children;
		// }
	};

	int sz;
	Node * root;
public:

	SpatialTree<V>():sz{0},root{new Node()} {}
	SpatialTree<V>(vector<V> data):sz{0},root{new Node()}
	{
		//TODO
	}
	SpatialTree<V>(V *data_ptr, int size):sz{0},root{new Node()}
	{
		//TODO
	}

	~SpatialTree<V>()
	{
		if (root != nullptr)
		{
			delete root;
		}
	}


};