#include <vector>
#include <utility>
#include <cmath>
#ifndef SPATIALGRID
#define SPATIALGRID

using std::vector;
using std::pair;
using std::make_pair;

typedef unsigned int Index;
typedef pair<double,double> XYPair;

struct IndexPair {
	Index i, j;

	IndexPair(const Index &x, const Index &y):i{x},j{y} {}
};

struct StructPair
{
	double x;
	double y;

	StructPair():x{0},y{0} {}

	StructPair(const double &xx, const double &yy):x{xx},y{yy} {}
	StructPair(const XYPair& i):x{i.first},y{i.second} {}
	StructPair operator+(const StructPair &other) const {
		return StructPair(x+other.x,y+other.y);
	}
	StructPair operator-(const StructPair &other) const {
		return StructPair(x-other.x,y-other.y);
	}
	StructPair operator*(const double &other) const {
		return StructPair(x*other,y*other);
	}
	StructPair operator/(const double &other) const {
		return StructPair(x/other,y/other);
	}
	double magnitude() const {
		return sqrt(x*x+y*y);
	}
};

XYPair asXYPair(const StructPair &i) {
	return make_pair(i.x,i.y);
}

class SpatialGrid 
{
public:

	virtual	vector<pair<int,int>> find_within( double &x, double &y, double &r) = 0;
	virtual unsigned int find_within_count(double &x, double &y, double &r) = 0;
	virtual bool clear() = 0;
	virtual unsigned int size() = 0;
};



#endif
