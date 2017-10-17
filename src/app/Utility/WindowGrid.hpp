#include <vector>
#include <utility>
#include <stdlib.h>
#include <cmath>
#include <cfloat>
#include <iostream>


#include "SpatialGrid.hpp"

#ifndef WINDOWGRID
#define WINDOWGRID

#define DEFAULT_DIMENSIONS 0.01

using namespace std;

template <typename Grid>
class WindowGrid: public SpatialGrid
{
private:
	double* rawData;


	Index sz;

	int w;
	int h;

	int node_count;

	Grid grid;

	XYPair windowTL;
	XYPair windowBR;

	XYPair datasetTL;
	XYPair datasetBR;

	XYPair windowHW;
	XYPair datasetHW;

	static inline void printPair(const XYPair & i)
	{
//		cout << get<0>(i) << "," << get<1>(i) << "\n";
	}


	static inline XYPair get_diff(XYPair &c1, XYPair &c2)
	{
		double dy = get<1>(c2)-get<1>(c1);
		double dx = get<0>(c2)-get<0>(c1);
		return make_pair(dx,dy);
	}


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
		double maxX = -DBL_MAX;
		double minY = DBL_MAX;
		double maxY = -DBL_MAX;
		rawData = new double[sz*2];
		for (int x = 0; x < w; ++x)
		{
			for (int y = 0; y < h; ++y)
			{
				int i = (x*w+y);
				rawData[2*i] = xx[i];
				rawData[2*i+1] = yy[i];
				minX = min(xx[i],minX);
				minY = min(yy[i],minY);
				maxX = max(xx[i],maxX);
//				if (yy[i] > maxY) {//cout << "REPLACING "; maxY = yy[i];}
				maxY = max(yy[i],maxY);
			}
		}
		datasetTL = make_pair(minX,maxY);
		datasetBR = make_pair(maxX,minY);
		datasetHW = make_pair(maxX-minX,maxY-minY);
	}

	void window_into(XYPair c1, XYPair c2)
	{
		auto windowCorners = getCorners(c1,c2);
		windowTL = get<0>(windowCorners);
		windowBR = get<1>(windowCorners);
		windowHW = make_pair(get<0>(windowBR)-get<0>(windowTL),get<1>(windowTL)-get<1>(windowBR));
		printPair(windowTL);
		printPair(windowBR);
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
				else {
				}
			}
		}
		relX.shrink_to_fit();
		relY.shrink_to_fit();
		double scaleNum = get<0>(windowHW)/get<0>(datasetHW)*get<1>(windowHW)/get<1>(datasetHW);
//		cout << "Scale num " << (unsigned long) scaleNum << "\n";
//		cout << "Wants to allocate " << 2*relX.size() << " and " << node_count*scaleNum << " \n";
		grid = Grid(relX.data(),relY.data(),relX.size(),1,2,node_count*scaleNum);
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
		windowHW = make_pair(0.0,0.0);
		w = 0;
		h = 0;
		node_count = 1;

	}

	WindowGrid(double* xx, double* yy, int hh, int ww, int node_cnt)
	{
		rawData = new double[10];
		localize_data(xx,yy,hh,ww);
		node_count = node_cnt;
		auto dSetDims = make_pair(get<0>(datasetBR)-get<0>(datasetTL), get<1>(datasetTL) - get<1>(datasetBR));
		auto windowDims = make_pair(get<0>(dSetDims)*DEFAULT_DIMENSIONS,get<1>(dSetDims)*DEFAULT_DIMENSIONS);
		// translate_window_to(datasetTL);
		// translate_window_to(make_pair(0,0));
		// reshape_window_to(windowDims); //Can optimize with lazy evaluation
	}

	WindowGrid(const WindowGrid<Grid> &other)
	{
		datasetBR = other.datasetBR;
		datasetTL = other.datasetTL;
		windowTL = other.windowTL;
		windowBR = other.windowBR;
		node_count = other.node_count;
		windowHW = other.windowHW;
		datasetHW = other.dataset.HW;
		w = other.w;
		h = other.h;
		sz = other.sz;
		delete [] rawData;
		rawData = new double[w*h*2];
		for (int i=0; i < w*h*2; ++i)
		{
			rawData[i] = other.rawData[i];
		}
//		window_into(windowTL,windowBR);
	}
	WindowGrid<Grid> &operator=(const WindowGrid<Grid> &other)
	{
		datasetBR = other.datasetBR;
		datasetTL = other.datasetTL;
		windowTL = other.windowTL;
		windowBR = other.windowBR;
		node_count = other.node_count;
		windowHW = other.windowHW;
		datasetHW = other.datasetHW;
		w = other.w;
		h = other.h;
		sz = other.sz;
		delete [] rawData;
		rawData = new double[w*h*2];
		for (int i=0; i < w*h*2; ++i)
		{
			rawData[i] = other.rawData[i];
		}
//		window_into(windowTL,windowBR);
		return *this;
	}

	~WindowGrid() 
	{
		delete [] rawData;
	}

    virtual vector<pair<int,int>> find_within( double &x, double &y, double &r)
	{
		// cout << "WARNING: \nWARNING: DEPERECATED FUNCTION CALL\nWARNING: \n";
		vector<pair<int,int>> ret;
		return ret;
	}

    virtual unsigned int find_within_count(double &x, double &y, double &r)
	{
		if (r > get<0>(windowHW))
		{
		//	cout << "Radius too large. Have to rescale window\n";
			reshape_window_to(make_pair(2*r,get<1>(windowHW)));
		}
		if (r > get<1>(windowHW))
		{
		//	cout << "Radius too large in Y. Have to rescale window\n";
			reshape_window_to(make_pair(get<0>(windowHW),2*r));
		}
		if (!check_overlap(windowTL,windowBR,x,y,r))
		{
		//	cout << "Need to shift window\n";
			translate_window_to(make_pair(x,y));
		}
		return grid.find_within_count(x,y,r);
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


	// XYPair windowTL;
	// XYPair windowBR;

	// XYPair datasetTt;
	// XYPair datasetBR;



	bool translate_window_to(const XYPair &center)
	{
		//Evaluate lazily?
		XYPair dims = get_diff(windowBR,windowTL);
		dims = make_pair(abs(get<0>(dims))/2.0,abs(get<1>(dims))/2.0);
		windowTL = make_pair(get<0>(center)-get<0>(dims),get<1>(center)+get<1>(dims));
		windowBR = make_pair(get<0>(center)+get<0>(dims),get<1>(center)-get<1>(dims));
		window_into(windowTL,windowBR);
		return true;
	}

	bool reshape_window_to(const XYPair &dimensions)
	{
		//Evaluate lazily?
		windowHW = dimensions;
		double cx = (get<0>(windowBR)+get<0>(windowTL))/2.0;
		double cy = (get<1>(windowBR)+get<1>(windowTL))/2.0;
		printPair(dimensions);
		windowTL = make_pair(cx-get<0>(dimensions)/2.0,cy+get<1>(dimensions)/2.0);
		windowBR = make_pair(cx+get<0>(dimensions)/2.0,cy-get<1>(dimensions)/2.0);
		printPair(windowTL);
		printPair(windowBR);
		window_into(windowTL,windowBR);
		return true;
	}

	bool set_corners(const XYPair &tl, const XYPair &br) {
		windowTL = tl;
		windowBR = br;
		window_into(windowTL,windowBR);
		return true;
	}
};



#endif

