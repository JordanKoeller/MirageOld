#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>



template<typename T>
class GridMap
{
	

	vector<vector<T>> rawData;
	unordered_map<T> buckets;
private:
	class Node
	{
	public:
		vector<T*> data;
	};
public:
};