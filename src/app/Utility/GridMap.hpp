#include <vector>
#include <cmath>
#include <iostream>
#include <utility>
#include <algorithm>
#include <cfloat>



template<typename T>
class GridMap
{
	
	T* rawData;
	unordered_map<int,unordered_map<int,Node>> buckets;
private:
	class Node
	{
	public:
		vector<T*> data;
	};
public:
};