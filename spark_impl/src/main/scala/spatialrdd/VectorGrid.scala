package spatialrdd
import scala.collection.mutable
import scala.util.Random

class VectorGrid(private val data: IndexedSeq[(Double, Double)], val partitionIndex: Int, val bucketFactor: Int) extends SpatialData {

  private val _hashX = equalHashing(data, (l: (Double, Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
  private val _hashY = equalHashing(data, (l: (Double, Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
  private val _buckets = _initBuckets()
  private def _initBuckets(): Array[Array[mutable.ListBuffer[Int]]] = {
    val numBucs = math.sqrt(data.size).toInt * bucketFactor
    Array.fill(numBucs)(Array.fill(numBucs)(mutable.ListBuffer[Int]()))
  }

  for (i <- 0 until data.size) _insert_pt(i)

  private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    new XYIntPair(x, y)
  }

  private def _fetch_bucket(i: Int, j: Int): Int = {
    try {
      _buckets(i)(j).size
    } catch {
      case e: ArrayIndexOutOfBoundsException => 0
    }
  }

  private def _query_bucket(i: Int, j: Int, x: Double, y: Double, r2: Double): Int = {
    try {
      if (_buckets(i)(j).size > 0) {
        var counter = 0
        for (k <- _buckets(i)(j)) {
          val pt = data(k)
          val dx = pt._1 - x
          val dy = pt._2 - y
          if (r2 >= dx * dx + dy * dy) counter += 1
        }
        counter
      } else 0
    } catch {
      case e: ArrayIndexOutOfBoundsException => 0
    }
  }

  private def _insert_pt(index: Int): Unit = {
    val coords = _hashFunction(data(index)._1, data(index)._2)
    _buckets(coords.x)(coords.y) += index
  }

  override def size: Int = data.size

  override def query_point_count(x: Double, y: Double, r: Double): Int = {
    val left = _hashFunction(x - r, y - r)
    val center = _hashFunction(x, y)
    val right = _hashFunction(x + r, y + r)
    val intR = new XYIntPair(center.x - left.x, center.y - left.y)
    val hypot2 = intR.x * intR.x + intR.y * intR.y
    val r2 = r * r
    var counter = 0
    counter += _query_bucket(center.x, center.y, x, y, r2) //Query center

    for (i <- 1 to intR.x + 2) { //Query x - axis
      counter += _query_bucket(center.x + i, center.y, x, y, r2)
      counter += _query_bucket(center.x - i, center.y, x, y, r2)
    }
    for (i <- 1 to intR.y + 2) {
      counter += _query_bucket(center.x, center.y + i, x, y, r2)
      counter += _query_bucket(center.x, center.y - i, x, y, r2)
    }


    for (i <- 1 to intR.x + 2) {
      val intRY = (math.sqrt(hypot2 - i * i)).toInt
      for (j <- 1 to intRY + 2) {
        counter += _query_bucket(center.x + i, center.y + j, x, y, r2)
        counter += _query_bucket(center.x + i, center.y - j, x, y, r2)
        counter += _query_bucket(center.x - i, center.y + j, x, y, r2)
        counter += _query_bucket(center.x - i, center.y - j, x, y, r2)
      }
    }
    counter
  }

  override def query_points(pts: Iterator[(XYIntPair, XYDoublePair)], r: Double): Iterator[(XYIntPair, Int)] = {
    pts.map(pt => pt._1 -> query_point_count(pt._2.x, pt._2.y, r))
  }
}

object VectorGrid {

  val bucketFactor = 1

  def apply(data: IndexedSeq[(Double, Double)], partitionIndex: Int): VectorGrid = {
    val ret = new VectorGrid(data, partitionIndex,bucketFactor)
    ret
  }

  def TestGrid() = {
  }
}
