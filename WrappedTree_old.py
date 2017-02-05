from scipy import spatial as sp
from Vector2D import Vector2D
import time

class WrappedTree(object):
	"Spatial Tree map data structure. Based on the Scipy spatial tree algorithms."
	def __init__(self):
		self.map = {}

	def __extractTuple(self,num):
		return (num.x,num.y)

	def setDataFromNumpy(self,data):
		for i in range(0,data.shape[0]):
			for j in range(0,data.shape[1]):
				k = (data[i,j].x,data[i,j].y)
				v = complex(i,j)
				self.map[k] = v
		self.keys = [*self.map.keys()]
		self.tree = sp.cKDTree(self.keys)
	def setDataFromNumpies(self,data):
		dataX = data[0]
		dataY = data[1]
		for i in range(0,dataX.shape[0]):
			for j in range(0,dataY.shape[1]):
				k = (dataX[i,j],dataY[i,j])
				v = (i,j)
				# print(str(v[0]) + "," + str(v[1]) + " from " + str(k[0]) + "," + str(k[1]))
				self.map[k] = v
		self.keys = [*self.map.keys()]
		lsz = 256
		self.tree = sp.cKDTree(self.keys,compact_nodes = False, balanced_tree = False, leafsize = lsz)



	def query_point(self,posx,posy,radius):
		"Query the tree for objects within the radius of a given point. Returns a list of pertinent objects."
		keys = self.tree.query_ball_point([posx,posy],radius)
		ret = []
		for i in keys:
			# print(i)
			# print(self.map[self.keys[i]])
			ret.append(self.map[self.keys[i]])
		# print("Done")
		return ret

	def  query_point_count(self,posx,posy,radius):
		return len(self.tree.query_ball_point([posx,posy],radius))
	