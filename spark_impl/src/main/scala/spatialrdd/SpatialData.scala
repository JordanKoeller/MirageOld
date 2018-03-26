package spatialrdd

trait SpatialData extends Serializable {
  


	def size:Int
	def query_point_count(x:Double, y:Double, r:Double):Int
	def query_points(pts:Iterator[((Int,Int),(Double,Double))], r:Double):Iterator[((Int,Int),Int)]
}

//object SpatialData {
//  class Ray(val index:Int) extends AnyVal {
//    
//  }
//  
//}

// object SpatialData {
//   def TestGrid() = {
//     val arr = Array.fill(500000)((Random.nextDouble()*100.0,Random.nextDouble()*100.0))
//     val grid = VectorGrid(arr)
//     (for (i <- 25 until 75; j <- 25 until 75) yield grid.query_point_count(i.toDouble,j.toDouble,5.0)).take(20) foreach println
//   }
	
// }
