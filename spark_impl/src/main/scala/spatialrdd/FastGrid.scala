package spatialrdd
import scala.collection.mutable
import scala.util.Random 

class OptGrid(private val data: IndexedSeq[(Double,Double)], bucketFactor: Int = 1) extends SpatialData {
  private val _buckets: mutable.HashMap[Int, mutable.HashMap[Int, mutable.Set[Int]]] = collection.mutable.HashMap()
  private val _hashX = equalHashing(data, (l: (Double,Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
  private val _hashY = equalHashing(data, (l: (Double,Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
  
  if (data.size > 0) {
    	  for (i <- 0 until data.size) _insert_pt(i)
  }

  private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    new XYIntPair(x, y)
  }

  private def _fetch_bucket(i:Int,j:Int):Int = {
    if (_buckets.contains(i) && _buckets(i).contains(j)) _buckets(i)(j).size
    else 0
  }

  private def _query_bucket(i:Int,j:Int,x:Double,y:Double, r2:Double):Int = {
    if (_buckets.contains(i) && _buckets(i).contains(j)) {
      var counter = 0
      for (k <- _buckets(i)(j)) {
        val pt = data(k)
        val dx = pt._1 - x
        val dy = pt._2 - y
        if (r2 >= dx*dx +dy*dy) counter += 1
      }
      counter
    }
    else 0
  }


  protected def _insert_pt(index: Int): Unit = {
    val coords = _hashFunction(data(index)._1, data(index)._2)
    if (!_buckets.contains(coords.x)) _buckets(coords.x) = mutable.HashMap[Int,mutable.Set[Int]]()
    if (!_buckets(coords.x).contains(coords.y)) _buckets(coords.x)(coords.y) = mutable.Set[Int]()
    _buckets(coords.x)(coords.y) += index
  }

  override def size:Int = data.size

  override def query_point_count(x: Double, y: Double, r: Double): Int = {
    val left = _hashFunction(x - r, y - r)
    val center = _hashFunction(x,y)
    val right = _hashFunction(x+r,y+r)
    val intR = new XYIntPair(center.x - left.x, center.y - left.y)
    val hypot2 = intR.x*intR.x+intR.y*intR.y
    val r2 = r*r
    var counter = 0
    for (i <- 1 until intR.x) {
      counter += _fetch_bucket(center.x+i,center.y)
      counter += _fetch_bucket(center.x-i,center.y)
    }
    for (i <- 1 until intR.y) {
      counter += _fetch_bucket(center.x,center.y+i)
      counter += _fetch_bucket(center.x,center.y-i)
    }
    counter += _fetch_bucket(center.x,center.y)
    for (i <- 1 to intR.x) {
      val intRY = (math.sqrt(hypot2-i*i)+1).toInt
      for (j <- 1 to intRY) {
        if (i < intR.x && j < intRY) {
          counter += _fetch_bucket(center.x+i,center.y+j)
          counter += _fetch_bucket(center.x+i,center.y-j)
          counter += _fetch_bucket(center.x-i,center.y-j)
          counter += _fetch_bucket(center.x-i,center.y+j)
        }
        else {
          counter += _query_bucket(center.x+i,center.y+j,x,y,r2)
          counter += _query_bucket(center.x+i,center.y-j,x,y,r2)
          counter += _query_bucket(center.x-i,center.y+j,x,y,r2)
          counter += _query_bucket(center.x-i,center.y-j,x,y,r2)
        }
      }
    }
    counter 
  }

  override def query_points(pts: Iterator[(XYIntPair,XYDoublePair)], r: Double): Iterator[(XYIntPair,Int)] = {
    pts.map(pt => pt._1 -> query_point_count(pt._2.x, pt._2.y, r))
  }
}

object OptGrid {

  val bucketFactor = 7

  def apply(data: IndexedSeq[(Double, Double)]): OptGrid = {
    val ret = new OptGrid(data, bucketFactor)
    ret
  }



  def TestGrid() = {
    val arr = Array.fill(500000)((Random.nextDouble()*100.0,Random.nextDouble()*100.0))
    val grid = OptGrid(arr)
    (for (i <- 25 until 75; j <- 25 until 75) yield grid.query_point_count(i.toDouble,j.toDouble,5.0)).take(20) foreach println
  }
}
