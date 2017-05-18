#include <vector>
#include <iostream>
#include <utility>
#include <cmath>

#include "Grid.hpp"

using namespace std;


int GridTests(vector<pair<pair<double,double>,pair<int,int>>> &data)
{
	Grid g (data.begin(),data.end(),2000);
	cout << "Done constructing \n";
	for (int i = 1; i < 200; ++i)
	{
		g.find_within(i/1000,i/15000,log(i));
		// cout << "Timed"
	}
	// g.printGrid();
	// g.debug();
	return 0;
}


int main(int argc, char const *argv[])
{
	// Point a {4.3,3.2};
	vector<pair<pair<double,double>,pair<int,int>>> data;
	for (int i = 1; i < 2000; ++i)
	{
		for (int j = 1; j < 2000; ++j)
		{
			data.push_back(make_pair(make_pair(sqrt(i),log(j)),make_pair(i,j)));
		}
	}

	GridTests(data);

	// cout << a.x << "," << a.y << endl;
	cout << "Test complete \n";
	return 0;
}