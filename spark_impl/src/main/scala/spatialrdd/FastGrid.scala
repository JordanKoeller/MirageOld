package spatialrdd
import scala.collection.mutable

class OptGrid(data: IndexedSeq[XYDoublePair], bucketFactor: Int = 1) extends Serializable {
  private val _buckets: mutable.HashMap[Int, mutable.HashMap[Int, mutable.Set[Int]]] = collection.mutable.HashMap()
  private val _hashX = equalHashing(data, (l: XYDoublePair) => l.x, math.sqrt(data.size).toInt * bucketFactor)
  private val _hashY = equalHashing(data, (l: XYDoublePair) => l.y, math.sqrt(data.size).toInt * bucketFactor)
  for (i <- 0 until data.size) _insert_pt(i)

  private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    new XYIntPair(x, y)
  }

  private def _fetch_bucket(i:Int,j:Int):Int = {
    if (_buckets.contains(i) && _buckets(i).contains(j)) _buckets(i)(j).size
    else 0
  }

  private def _query_bucket(i:Int,j:Int,x:Double,y:Double, r:Double):Int = {
    if (_buckets.contains(i) && _buckets(i).contains(j)) {
      var counter = 0
      for (k <- _buckets(i)(j)) {
        val pt = data(k)
        val dx = pt.x - x
        val dy = pt.y - y
        if (r*r >= dx*dx +dy*dy) counter += 1
      }
      counter
    }
    else 0
  }


  private def _insert_pt(index: Int): Unit = {
    val coords = _hashFunction(data(index).x, data(index).y)
    if (!_buckets.contains(coords.x)) _buckets(coords.x) = mutable.HashMap[Int,mutable.Set[Int]]()
    if (!_buckets(coords.x).contains(coords.y)) _buckets(coords.x)(coords.y) = mutable.Set[Int]()
    _buckets(coords.x)(coords.y) += index
  }

  def size = data.size

  def query_point_count(x: Double, y: Double, r: Double): Int = {


    val left = _hashFunction(x - r, y - r)
    val center = _hashFunction(x,y)
    val intR = _hashFunction(r,r)
    val hypot2 = intR.x*intR.x+intR.y*intR.y
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
      val intRY = (math.sqrt(hypot2-i*i)+2).toInt
      for (j <- 1 to intRY) {
        if (i < intR.x) {
          counter += _fetch_bucket(center.x+i,center.y+j)
          counter += _fetch_bucket(center.x+i,center.y-j)
          counter += _fetch_bucket(center.x-i,center.y-j)
          counter += _fetch_bucket(center.x-i,center.y+j)
        }
        else {
          counter += _query_bucket(center.x+i,center.y+j,x,y,r)
          counter += _query_bucket(center.x+i,center.y-j,x,y,r)
          counter += _query_bucket(center.x-i,center.y+j,x,y,r)
          counter += _query_bucket(center.x-i,center.y-j,x,y,r)
        }
      }
    }
    counter 
  }

  def query_points(pts: Iterator[XYDoublePair], r: Double): Iterator[Int] = {
    pts.map(pt => query_point_count(pt.x, pt.y, r))
  }
}

object OptGrid {

  val bucketFactor = 7

  def apply(data: IndexedSeq[(Double, Double)]): OptGrid = {
    val ret = new OptGrid(data.map(pt => new XYDoublePair(pt._1, pt._2)), bucketFactor)
    ret
  }
}
