#include <vector>
#include <utility>
#include "SpatialGrid.hpp"

#ifndef WINDOWGRID
#define WINDOWGRID

#define DEFAULT_DIMENSIONS 0.1

using namespace std;

template <typename Grid>
class WindowGrid: public SpatialGrid
{
private:
	double* rawData;


	Index sz;

	int w;
	int h;

	Grid grid;

	XYPair windowTL;
	XYPair windowBR;

	XYPair datasetTL;
	XYPair datasetBR;


	static inline pair<XYPair, XYPair> getCorners(XYPair &c1, XYPair &c2)
	{
		double tlx = min(get<0>(c1),get<0>(c2));
		double brx = max(get<0>(c1),get<0>(c2));
		double tly = max(get<1>(c1),get<1>(c2));
		double bry = min(get<1>(c1),get<1>(c2));
		return make_pair(make_pair(tlx,tly),make_pair(brx,bry));
	}

	static inline bool pt_within_box(XYPair &pt, XYPair &tl, XYPair &br)
	{
		return (get<0>(tl) <= get<0>(pt) &&
				get<0>(br) >= get<0>(pt) &&
				get<1>(tl) >= get<1>(pt) &&
				get<1>(br) <= get<1>(pt));

	}

	void localize_data(double* xx, double* yy, int ww, int hh)
	{
		delete [] rawData;
		w = ww;
		h = hh;
		sz = w*h;
		double minX = DBL_MAX;
		double maxX = DBL_MIN;
		double minY = DBL_MAX;
		double maxY = DBL_MIN;
		rawData = new double[sz*2];
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				Index i = (x*w+h);
				rawData[2*i] = xx[i];
				rawData[2*i+1] = yy[i];
				minX = min(xx[i],minX);
				minY = min(yy[i],minY);
				maxX = max(xx[i],maxX);
				maxY = max(yy[i],maxY);
			}
		}
		datasetTL = make_pair(minX,maxY);
		datasetBR = make_pair(maxX,minY);
	}

	void window_into(XYPair c1, XYPair c2)
	{
		auto windowCorners = getCorners(c1,c2);
		windowTL = get<0>(windowCorners);
		windowBR = get<1>(windowCorners);
		vector<double> relX;
		vector<double> relY;
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				Index i = 2*(x*w+y);
				XYPair pt = make_pair(rawData[i],rawData[i+1]);
				if (pt_within_box(pt,windowTL,windowBR))
				{
					relX.push_back(get<0>(pt));
					relY.push_back(get<1>(pt));
				}
			}
		}
	}


	/**********************************************************************
        *******							    ***********
	******* Some Helper functions for checking is within window ***********
	*******                                                     ***********
	**********************************************************************/
	
	/***********************************************************
	******* Checks to see if circle is entirely enclosed********
	***********************************************************/

    static bool check_overlap(XYPair &tl, XYPair &br,
	double x, double y, double r)
	{
		return (x - get<0>(tl) >= r &&
				get<0>(br) - x >=r &&
				get<1>(tl) - y >= r && 
				y - get<1>(br) >= r);
	}

public:

	WindowGrid()
	{
		sz = 0;
		rawData = new double[10];
		grid = Grid();
		windowTL = make_pair(0.0,0.0);
		windowBR = make_pair(0.0,0.0);
		w = 0;
		h = 0;

	}

	WindowGrid(double* xx, double* yy, int h, int w, int node_count)
	{
		rawData = new double[10];
		localize_data(xx,yy,h,w);
		auto dSetDims = make_pair(get<0>(datasetBR)-get<0>(datasetTL), get<1>(datasetTL) - get<1>(datasetBR));
		auto windowDims = make_pair(get<0>(dSetDims)*DEFAULT_DIMENSIONS,get<1>(dSetDims)*DEFAULT_DIMENSIONS);
		reshape_window_to(windowDims);
		translate_window_to(datasetTL);
	}

	~WindowGrid() 
	{
		delete [] rawData;
	}

    virtual vector<pair<int,int>> find_within( double &x, double &y, double &r)
	{
		vector<pair<int,int>> ret;
		return ret;
	}

    virtual unsigned int find_within_count(double &x, double &y, double &r)
	{
		if (check_overlap(windowTL,windowBR,x,y,r))
		{
			return grid.find_within_count(x,y,r);
		}
		else 
		{
			cout << "Need to shift window\n";
			translate_window_to(make_pair(x,y));
			return 0;
		}
	}

    virtual bool clear()
	{
		grid.clear();
		delete [] rawData;
		rawData = new double[10];
		return 1;
	}

    virtual unsigned int size()
	{
		return sz;
	}

	bool translate_window_to(const XYPair &center)
	{
		//Evaluate lazily?
		return false;
	}

	bool reshape_window_to(const XYPair &dimensions)
	{
		//Evaluate lazily?
		return false;
	}
};


#endif

