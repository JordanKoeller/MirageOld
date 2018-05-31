#include <vector>
#include <utility>

#include "SpatialGrid.hpp"

using std::vector;
using std::pair;

class kDTree: public SpatialGrid
{
private:
	struct Node {
		double * data;
		Node * parent;
		Node * left;
		Node * right;
		XYPair tl;
		XYPair br;
	};

	Node * root;

	static Index recurs_search_count(const Node &n,const double &x,const double &y,const double &r) {
		return 0;
	}
public:
	kDTree():root{nullptr} {}
	kDTree(double * x, double *y, Index length, Index bucket_count) {
		root = nullptr;
	}
	~kDTree()=default;
	vector<pair<int,int>> find_within( double &x, double &y, double &r) {
		vector<pair<int,int>> ret {1};
		return ret;
	}
	unsigned int find_within_count(double &x, double &y, double &r) {
		return 0;
	}
	bool clear() {
		return true;
	}
	unsigned int size() {
		return 0;
	}

	
};