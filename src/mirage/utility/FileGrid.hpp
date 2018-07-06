

#include "SpatialGrid.hpp"
#include <vector>
#include <utility>
#include <string>
#include <map>
#include <cstdio>
#include <iostream>
#include <cfloat>
#include <cmath>
#include <unordered_set>
using std::map;
using std::vector;
using std::unordered_set;
using std::pair;
using std::string;
using std::min;
using std::max;
using std::abs;
using std::cout;
using std::endl;

struct Box {
	Index shift;
	Index size;
	Index current_adder;

	Box(Index sz, Index sh):shift{sh},size{sz},current_adder{0} {}
	Box():shift{0},size{0},current_adder{0} {}
};

struct Row
{
	Box box;
	Index i;
	Index j;

	Row(const Index ii, const Index jj,const Box &b):box{b},i{ii},j{jj} {}
	Row():i{0},j{0} {}
};

struct Lookup_Table {
	virtual Box get_box(const Index &i, const Index &j) = 0;
	virtual bool set_box(const Index &i, const Index &j, const Box &b) = 0;
	virtual FILE * write_file(FILE *f) = 0;
	virtual FILE * from_file(FILE *f) =0;
	virtual Index size_of()=0;
	virtual bool contains(const Index &i, const Index &j) = 0;
	virtual bool set_shifts() = 0;
};

struct MapLookup
{
	Index w;
	map<Index,Box> lookup;

	Box get_box(const Index &i, const Index &j) {
		return lookup[i*w+j];
	}

	bool contains(const Index &i, const Index &j) {
		return lookup.find(i*w+j) != lookup.end();
	}

	bool set_box(const Index &i, const Index &j, const Box b) {
		// cout << "setting "  << i << "," << j <<endl;
		lookup[i*w+j] = b;
		return true;
	}

	bool set_shifts() {
		vector<Row> rows = vector<Row>(lookup.size());
		for (auto row_pair:lookup) {
			if (row_pair.second.size != 0) {
				auto ind = row_pair.first;
				auto box = row_pair.second;
				auto row = Row(ind / w, ind % w, box);
				rows.push_back(row);
			}
		}
		Index rover = 0;
		for (auto row:rows) {
			Box b = get_box(row.i,row.j);
			b.shift = rover;
			rover += sizeof(StructPair)*b.size;
			set_box(row.i,row.j,b);
		}
		return true;
	}

	FILE * write_file(FILE *f) {
		//TODO
		Index lookup_size = lookup.size();
		fwrite(&lookup_size,sizeof(Index),1,f);
		fwrite(&w,sizeof(Index),1,f);
		Row *rows = new Row[lookup_size];
		Index rover = 0;
		for (auto row_pair:lookup) {
			if (row_pair.second.size != 0) {
				auto ind = row_pair.first;
				auto box = row_pair.second;
				auto row = Row(ind / w, ind % w, box);
				rows[rover++] = row;
			}
		}
		fwrite(rows,sizeof(Row),rover,f);
		delete [] rows;
		return f;
	}

	FILE * from_file(FILE *f) {
		lookup.clear();
		Index lookup_size;
		fread(&lookup_size,sizeof(Index),1,f);
		fread(&w,sizeof(Index),1,f);
		Row *rows = new Row[lookup_size];
		fread(rows,sizeof(Row),lookup_size,f);
		if (lookup_size != 0) {
			for (Index i =0; i < lookup_size; i++) {
				set_box(rows[i].i,rows[i].j,rows[i].box);
			}
		}
		delete [] rows;
		return f;
	}

	Index size_of() {
		return sizeof(Row)*lookup.size() + sizeof(Index)*2;
	}

	MapLookup(const Index width):w{width} {}
	MapLookup()=default;

	void print() {
		int c = 0;
		for (auto row_pair:lookup) {
			if (row_pair.second.size != 0) {
				auto ind = row_pair.first;
				auto box = row_pair.second;
				auto row = Row(ind / w, ind % w, box);
				// cout << row.i << "," << row.j << " : " << row.box.size << "," << row.box.shift << endl;
				c += row.box.size;
			}
		}
		cout << "Total count of " << c << endl;
	}

};


class FileGrid : public SpatialGrid
{
private:
	struct Grid_Properties
	{
		double tlx, tly, NODE_WIDTH, NODE_HEIGHT;
		Index sz, root_buckets;
	};

	typedef MapLookup Table;
	//Deleted Methods:
	FileGrid(const FileGrid& that) = delete;
	FileGrid operator=(const FileGrid& that) = delete;

	//Data members
	FILE * f;

	Table table;
	Grid_Properties properties;

	// map<Index,Node> node_buffer;


	/* FILE LAYOUT IS AS FOLLOWS: 
		
		HEAD-----------------------------------------------------------------
		properties-------------------sizeof(Grid_Properties)
		LOOKUPTABLE----------sizeof(Box)*num_boxes
		BOX_1----------------sizeof(StructPair)*BOX_1.size
		BOX_2----------------sizeof(StructPair)*BOX_2.size
		.
		.
		.
		BOX_{num_boxes}------sizeof(StructPair)*BOX_{num_boxes}.size
		END------------------------------------------------------------------



	In LOOKUPTABLE: layout is as follows:

			ROW LAYOUT
		+-------------+------------+
        | FILE_SHIFT  |  BOX_SIZE  |
        +-------------+------------+

        Where FILE_SHIFT is the pointer offset from the end of the LOOKUPTABLE. 
	*/


	//To allow for a memory-based or file-based lookup table, I template the lookup
	// table. The table just needs to have a method `get(Index,Index)` that
	//Allows for finding a specific box and returns the FILE_SHIFT and BOX_SIZE

	//*********************COMPUTATIONAL GEOMETRY******************************

	inline static bool isLeft(const StructPair &a,const StructPair &b, const StructPair &c)
	{
		//Tests if c is to the left of line ab
		return ((a.x - c.x)*(b.y-c.y)-(b.x-c.x)*(a.y-c.y)) < 0.0;
	}

	inline bool line_intersects(const StructPair &x, const StructPair &y, const StructPair &a, const StructPair &b) {
		return (isLeft(x,y,a) != isLeft(x,y,b)) && (isLeft(a,b,x) != isLeft(a,b,y));
	}


    inline bool overlaps_box(const vector<StructPair> &box,const vector<StructPair> &grid) {
    	//Two possibilities. Either a corner is inside the other, or the lines intersect.
    	//Can narrow to these two possibilities because We have rectangles only.

    	//Possibility 1: Must check if box in grid and if grid in box.
    	//Box in grid:
    	//Grid layout: [bl,tl, tr, br]
    	for (auto box_corner:box) {
    		if (grid[0].x <= box_corner.x && 
    			grid[0].y <= box_corner.y &&
    			grid[2].x >= box_corner.x &&
    			grid[2].y >= box_corner.y) {return true;}
    	}
    	//grid in box:
    	//Need to check left-of relations.
    	for (auto grid_corner:grid) {
    		if ((isLeft(box[0],box[1],grid_corner) != isLeft(box[2],box[3],grid_corner)) &&
    			(isLeft(box[1],box[2],grid_corner) != isLeft(box[3],box[0],grid_corner))) {return true;}
    	}

    	//check for line intersections:
    for (int k=0;k < 16;k++) {
    	int i = k % 4;
    	int j = k / 4;
    	if (line_intersects(box[i],box[(i+1)%4],grid[j],grid[(j+1)%4])) {return true;}

    }
    return false;
    
    }



    inline IndexPair get_indices(const double &x,const double &y)
    {
        Index xx  = round((((x) - properties.tlx)/properties.NODE_WIDTH));
        Index yy  = round((((y) - properties.tly)/properties.NODE_HEIGHT));
        return IndexPair(xx,yy);                
    }

    //(x-tx)/W = I
    //IW = (x-tx)
    // x = IW + tx

    inline StructPair box_coords(const Index &i, const Index &j) {
    	double x = ((double) i) * properties.NODE_WIDTH + properties.tlx;
    	double y = ((double) j) * properties.NODE_HEIGHT + properties.tly;
    	return StructPair(x,y);
    }

    inline double hypot2(const double &x1,const double &x2,const double &y1,const double &y2) {
    	double dx,dy;
    	dx = x2 - x1;
    	dy = y2 - y1;
    	return dx*dx + dy*dy;
    }


    vector<IndexPair> box_slice(const double &x1, const double &x2, const double &y1, const double& y2, const double &r) {
    	vector<IndexPair> ret;
    	const StructPair l1 {x1,y1};
    	const StructPair l2 {x2,y2};
    	const StructPair axis = l2 - l1;
    	const double line_length = axis.magnitude();
    	const double slice_length = line_length + 2.0*r;
    	const StructPair ortho_axis_r = StructPair(-axis.y,axis.x)*r/line_length;
    	const StructPair axis_r = axis*r/line_length;
    	const double slice_width = 2.0*r;
    	cout << "Area of " << slice_width*slice_length << endl;

    	//The four corners of the box. Winding, goes (p1 -> p2) -> (p3 -> p4) -> p1
    	//Groupings are of "short" sides
    	const StructPair p1 = l2 + axis_r + ortho_axis_r;
    	const StructPair p2 = l2 + axis_r - ortho_axis_r;
    	const StructPair p3 = l1 - axis_r - ortho_axis_r;
    	const StructPair p4 = l1 - axis_r + ortho_axis_r;
    	//Note that p1 and p3 are opposite
    	cout << "Difference is " << (p4 - p1).magnitude() - slice_length << endl; 
    	vector<StructPair> corners;
    	corners.push_back(p1);
    	corners.push_back(p2);
    	corners.push_back(p3);
    	corners.push_back(p4);
    	double span_x = 0.0, span_y = 0.0;
    	for (Index i = 0; i < 4; i++) {
    		span_x = max(span_x,abs(corners[i].x - corners[(i+1) % 4].x));
    		span_y = max(span_y,abs(corners[i].y - corners[(i+1) % 4].y));
    	}
    	const StructPair center = (l1 + l2) / 2.0;
    	const IndexPair center_I = get_indices(center.x,center.y);
    	const Index span_x_I = span_x/properties.NODE_WIDTH;
    	const Index span_y_I = span_y/properties.NODE_HEIGHT;
    	for (int i= (int) center_I.i - (int) span_x_I; i <= (int) span_x_I+ (int) center_I.i; i++) {
    		for (int j=(int) center_I.j - (int) span_y_I; j <= (int) span_y_I+(int) center_I.j; j++) {
    			if (i >= 0 && j >= 0 && i < (int) properties.root_buckets && j < (int) properties.root_buckets) {
	    			vector<StructPair> box;
	    			box.push_back(box_coords(i,j));
	    			box.push_back(box_coords(i,j+1));
	    			box.push_back(box_coords(i+1,j+1));
	    			box.push_back(box_coords(i+1,j));
	    			if (overlaps_box(corners,box)) {
	    				ret.push_back(IndexPair(i,j));
	    			}
    			}
    		}
    	}
    	cout << "Found " << ret.size() << " pairs" << endl;
    	cout << "Total number of buckets " << properties.root_buckets*properties.root_buckets << endl;
    	cout << "Percentage is " << ((double) ret.size())/((double) properties.root_buckets*properties.root_buckets) << endl;

    	return ret;

    }

	//*********************HELPER FUNCTIONS************************************




	// inline Index search_box_count(const double &x,const double &y,const double &r,const Box &box) {
	// 	StructPair* box_contents = new StructPair[box.size];
	// 	fseek(f,sizeof(properties) + table.size_of() + box.shift,SEEK_SET);
	// 	fread(box_contents,sizeof(StructPair),box.size,f);


	// delete [] box_contents;

	// }

	inline bool write_box_contents(const vector<StructPair> &points,const Index &i,const Index &j) {
		Box box = table.get_box(i,j);
		fseek(f,sizeof(properties) + table.size_of() + box.shift,SEEK_SET);
		StructPair * pairs = new StructPair[points.size()];
		for (Index i=0;i<points.size();i++) {
			pairs[i] = points[i];
		}
		fwrite(pairs,sizeof(StructPair),points.size(),f);
		delete [] pairs;
		return true;
	}

	inline bool add_point(const IndexPair &index,const StructPair &point) {
		Box box = table.get_box(index.i,index.j);
		fseek(f,sizeof(properties) + table.size_of() + box.shift + sizeof(Index)*box.current_adder,SEEK_SET);
		fwrite(&point,sizeof(StructPair),1,f);
		box.current_adder++;
		return true;
	}

	void write_headers() {
		fseek(f,0,SEEK_SET);
		fwrite(&properties,sizeof(Grid_Properties),1,f);

	}

public:
	FileGrid()=default;
	~FileGrid()=default;

	FileGrid(const string &filename) {
		f = fopen(filename.c_str(), "r+b");
		if (f == nullptr) { //Means the file already exists. Need to pull it out and set up its representation.
			f = fopen(filename.c_str(),"w+b");
		}
		cout <<"NEED TO UPDATE CONSTRUCTOR" << endl;
	}

	template<typename Container>
	FileGrid(const Container & stl, const string &filename, const Index num_boxes) {
		f = fopen(filename.c_str(),"w+b");
		const Index root_box = (Index) sqrt((double) num_boxes);
		properties.root_buckets = root_box;
		double min_x = DBL_MAX, min_y = DBL_MAX, max_x = -DBL_MAX, max_y = -DBL_MAX;
		StructPair elem;
		cout << "First for loop " <<endl;
		for (auto iter = stl.begin(); iter != stl.end(); iter++) {
			properties.sz++;
			elem = (*iter);
			max_x = max(max_x,elem.x);
			max_y = max(max_y,elem.y);
			min_x = min(min_x,elem.x);
			min_y = min(min_y,elem.y);
		}
		properties.NODE_WIDTH = (max_x - min_x)/((double) root_box);
		properties.NODE_HEIGHT = (max_y - min_y)/((double) root_box);
		properties.tlx = min_x;
		properties.tly = min_y;
		table = Table(properties.root_buckets);
		cout << "Second for loop " <<endl;
		for (auto iter = stl.begin(); iter != stl.end(); iter++) {
			elem = (*iter);
			Box b;
			auto index = get_indices(elem.x,elem.y);
			if (table.contains(index.i,index.j)) {
				b = table.get_box(index.i,index.j);
			}
			b.size++;
			// Index shift = sizeof(StructPair)*b.size;
			table.set_box(index.i,index.j,b);

		}
		table.set_shifts();
		table.print();
		cout << "Third for loop " <<endl;
		for (auto iter = stl.begin(); iter != stl.end(); iter++) {
			elem = (*iter);
			auto index = get_indices(elem.x,elem.y);
			add_point(index, elem);
		}
		write_headers();
		table.write_file(f);
	}




	vector<pair<int,int>> find_within( double &x, double &y, double &r) {
		vector<pair<int,int>> ret;
		return ret;
	}
	unsigned int find_within_count(double &x, double &y, double &r) {
		return 0;
	}
	bool clear() {
		return true;
	}
	unsigned int size() {
		return properties.sz;
	}

	void slice(const double &x1, const double &x2, const double &y1, const double& y2, const double &r) {
		box_slice(x1,x2,y1,y2,r);
	}
	
};


