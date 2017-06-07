#include <vector>
#include <iostream>
#include <utility>
#include <cmath>

#include "MapGrid.hpp"
using namespace std;


int main(int argc, char const *argv[])
{

	double* data;
	data = new double[100];
	for (int i = 0;i<50;i++) 
	{
		data[i] = ((double) i * 2 / 5) * 1.0/3.14;
		data[i+1] = ((double) i * 5 / 2) * 1.0/3.14159;
	}
	int sz = 10;
	Grid g = Grid(data, 5, 10, 2, sz);
	double four = 4.0;
	auto ret = g.find_within(data[7],data[7*5+1],four);

	cout << "Tests Done\n";
	return 0;
}
