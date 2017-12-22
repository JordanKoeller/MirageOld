#include <vector>
#include <utility>

#ifndef SPATIALGRID
#define SPATIALGRID

using std::vector;
using std::pair;

class SpatialGrid 
{
public:

	typedef unsigned int Index;
	typedef pair<double,double> XYPair;
	virtual	vector<pair<int,int>> find_within( double &x, double &y, double &r) = 0;
	virtual unsigned int find_within_count(double &x, double &y, double &r) = 0;
	virtual bool clear() = 0;
	virtual unsigned int size() = 0;
};



#endif
