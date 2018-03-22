package spatialrdd
import scala.collection.mutable

class MemGrid(grid: Array[Array[Array[(Double, Double)]]], _hashX: Double => Int, _hashY: Double => Int, sz: Int, val partitionIndex: Int) extends SpatialData {

  private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    new XYIntPair(x, y)
  }

  private def _query_bucket(i: Int, j: Int, x: Double, y: Double, r2: Double): Int = {
    if (i >= 0 && j >= 0 && i < grid.size && j < grid(i).size) {
      val lst = grid(i)(j)
      if (lst.size > 0) {
        var counter = 0
        var ind = 0
        var dx = 0.0
        var dy = 0.0
        while (ind < lst.size) {
          dx = lst(ind)._1 - x
          dy = lst(ind)._2 - y
          if (r2 >= dx * dx + dy * dy) counter += 1
          ind += 1
        }
        counter
      } else 0
    } else 0
  }
  
//  private def queryOptimized(x:Double, y:Double, r:Double): Int = {
//    var counter = 0
//    var i = 0
//    var j = 0
//    val center = _hashFunction(x,y)
//    var rx = _hashX(r)
//    var ry = _hashY(r)
//    while (rx >= 0) {
//      
//    }
//    ???
//  }

  override def query_point_count(x: Double, y: Double, r: Double): Int = {
    val left = _hashFunction(x - r, y - r)
    val center = _hashFunction(x, y)
    val right = _hashFunction(x + r, y + r)
    val intR = new XYIntPair(center.x - left.x, center.y - left.y)
    val hypot2 = intR.x * intR.x + intR.y * intR.y
    val r2 = r * r
    var counter = 0
    var i = 0
    var j = 0
    counter += _query_bucket(center.x, center.y, x, y, r2) //Query center

    while (i <= intR.x + 3) { //Query x - axis
      counter += _query_bucket(center.x + i, center.y, x, y, r2)
      counter += _query_bucket(center.x - i, center.y, x, y, r2)
      i += 1
    }
    i = 0
    while (i <= intR.y + 3) {
      counter += _query_bucket(center.x, center.y + i, x, y, r2)
      counter += _query_bucket(center.x, center.y - i, x, y, r2)
      i += 1
    }
    i = 0
    while (i <= intR.x + 3) {
      val intRY = (math.sqrt(hypot2 - i * i)).toInt
      while (j <= intRY + 3) {
        counter += _query_bucket(center.x + i, center.y + j, x, y, r2)
        counter += _query_bucket(center.x + i, center.y - j, x, y, r2)
        counter += _query_bucket(center.x - i, center.y + j, x, y, r2)
        counter += _query_bucket(center.x - i, center.y - j, x, y, r2)
        j += 1
      }
      i += 1
    }
    counter
  }

  override def query_points(pts: Iterator[(XYIntPair, XYDoublePair)], r: Double): Iterator[(XYIntPair, Int)] = {
    pts.map(pt => pt._1 -> query_point_count(pt._2.x, pt._2.y, r))
  }

  override def size: Int = sz

}

object MemGrid {

  val bucketFactor = 1
  def apply(data: IndexedSeq[(Double, Double)], partitionIndex: Int, bucketFactor: Int = bucketFactor): MemGrid = {
    val _hashX = equalHashing(data, (l: (Double, Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
    val _hashY = equalHashing(data, (l: (Double, Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
    val numBucs = math.sqrt(data.size).toInt * bucketFactor
    val grid = Array.fill(numBucs)(Array.fill(numBucs)(mutable.ListBuffer[(Double, Double)]()))
    var rover = 0
    while (rover < data.size) {
      val elem = data(rover)
      val x = _hashX(elem._1)
      val y = _hashY(elem._2)
      grid(x)(y) += elem
      rover += 1
    }
    new MemGrid(grid.map(_.map(_.toArray)), _hashX, _hashY, data.size, partitionIndex)
  }
}
