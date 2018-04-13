package spatialrdd
import utility.Index
import utility.IndexPair
import utility.DoublePair
trait SpatialData extends Serializable {
  


	def size:Int
	def query_point_count(x:Double, y:Double, r:Double):Int
	def query_points(pts:Iterator[((Int,Int),(Double,Double))], r:Double):Iterator[((Int,Int),Index)]
}


