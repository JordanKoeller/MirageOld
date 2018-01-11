package spatialrdd
import scala.collection.mutable

class SpatialGrid(data: IndexedSeq[XYDoublePair], bucketFactor: Int = 1, val partitionIndex:Int) extends Serializable {
  private val _buckets: mutable.HashMap[Int, mutable.HashMap[Int, mutable.Set[Int]]] = collection.mutable.HashMap()
  private val _hashX = equalHashing(data, (l: XYDoublePair) => l.x, (math.sqrt(data.size)*bucketFactor).toInt)
  private val _hashY = equalHashing(data, (l: XYDoublePair) => l.y, (math.sqrt(data.size)*bucketFactor).toInt)
  for (i <- 0 until data.size) _insert_pt(i)

  private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    new XYIntPair(x, y)
  }


  private def _insert_pt(index: Int): Unit = {
    val coords = _hashFunction(data(index).x, data(index).y)
    if (!_buckets.contains(coords.x)) _buckets(coords.x) = mutable.HashMap[Int,mutable.Set[Int]]()
    if (!_buckets(coords.x).contains(coords.y)) _buckets(coords.x)(coords.y) = mutable.Set[Int]()
    _buckets(coords.x)(coords.y) += index
  }

  def size = data.size

  def query_point_count(x: Double, y: Double, r: Double): Int = {

    //Lots of optimization to be done here!!

    val left = _hashFunction(x - r, y - r)
    val center = _hashFunction(x + r, y + r)
    var counter = 0
    for (i <- left.x to center.x) {
      for (j <- left.y to center.y) {
        for (k <- _buckets(i)(j)) {
          val pt = data(k)
          val dx = pt.x - x
          val dy = pt.y - y
          if (r * r >= dx * dx + dy * dy) {
            counter += 1
          }
        }
      }
    }

    counter
  }

  def query_points(pts: Iterator[XYDoublePair], r: Double): Iterator[Int] = {
    pts.map(pt => query_point_count(pt.x, pt.y, r))
  }
}

object SpatialGrid {

  val bucketFactor = 7

  def apply(data: IndexedSeq[(Double, Double)]): SpatialGrid = {
    println("Calling new SpatialGrid")
    val ret = new SpatialGrid(data.map(pt => new XYDoublePair(pt._1, pt._2)), bucketFactor)
    println("Finished calling new SpatialGrid")
    ret
  }
}
