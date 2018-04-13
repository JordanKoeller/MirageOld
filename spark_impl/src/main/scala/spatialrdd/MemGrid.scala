package spatialrdd
import scala.collection.mutable
import utility.DoublePair
import utility.Index
import math.sqrt

//class MemGrid(grid: Array[Array[mutable.ArrayBuffer[Double]]], _hashX: Double => Int, _hashY: Double => Int, sz: Int, val partitionIndex: Int) extends SpatialData {
class MemGrid(grid: mutable.Map[Index, mutable.Map[Index, mutable.ArrayBuffer[Double]]], hashXPair: (HashFunc, Dehasher), hashYPair: (HashFunc, Dehasher), sz: Int, extremes: (Double, Double, Double, Double)) extends SpatialData {

  private def _hashX = hashXPair._1

  private def _hashY = hashYPair._1

  private def _dehashX = hashXPair._2

  private def _dehashy = hashYPair._2

  private def _hashFunction(xx: Double, yy: Double): (Int, Int) = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    (x, y)
  }

  private def _query_bucket(center: (Int, Int), i: Int, j: Int, x: Double, y: Double, r2: Double): Int = {
    if (grid.contains(i + center._1) && grid(i + center._1).contains(center._2 + j)) {
      val queryType = query_type(center, i, j, r2, x, y)
 //     if (queryType == -1) 0
 //     else if (queryType == 1) grid(center._1 + i)(center._2 + j).size
 //     else if (queryType == 0 && grid(center._1 + i)(center._2 + j).size > 0) {
      var counter = 0
        var ind = 0
        var dx = 0.0
        var dy = 0.0
        while (ind < grid(center._1 + i)(center._2 + j).size) {
          dx = grid(center._1 + i)(center._2 + j)(ind) - x
          dy = grid(center._1 + i)(center._2 + j)(ind + 1) - y
          if (r2 >= dx * dx + dy * dy) counter += 1
          ind += 2
        }
        counter

 //     } else 0

   } else 0

    //    if (grid.contains(i) && grid(i).contains(j)) {
    //      } else 0
    //    } else 0
  }

  private def _fetch_bucket(i: Int, j: Int): Int = {
    if (grid.contains(i) && grid(i).contains(j)) {
      grid(i)(j).size / 2
    } else 0
  }

  private def query_type(center: (Int, Int), i: Int, j: Int, r2: Double, x: Double, y: Double): Int = {
    //First figure out the quadrant
    //Then know how to shift i and j to find which corners I need to check.
    var ret = 0
    var xShift = 0
    var yShift = 0
    if (i >= 0) xShift = 1 else xShift = -1
    if (j >= 0) yShift = 1 else yShift = -1
    ret += contains(x, y, center._1+i, center._2+j, r2)
    ret += contains(x, y, center._1 + xShift+i, center._2 + j, r2)
    ret += contains(x, y, center._1 + xShift+i, center._2 + yShift + j, r2)
    ret += contains(x, y, center._1 + i, center._2 + j + yShift, r2)
    if (ret == 4) 1 else if (ret == 0) -1 else 0
    //1 means all enclose
    //-1 means completely excluded
    //0 means partially enclosed
  }
  def intersects(x: Double, y: Double, r: Double): Boolean = {
    val flag1 = contains(x - r, y) || contains(x + r, y) || contains(x, y - r) || contains(x, y + r)
    //    val r2 = r*r
    //    val flag2 = radius2(extremes._1,extremes._2,pt._1,pt._2)
    true
    //NEEDS WORK
    //FIXME
  }
  private def contains(x: Double, y: Double): Boolean = {
    x > extremes._1 && x < extremes._2 && y > extremes._3 && y < extremes._4
  }

  private def radius2(x1: Double, x2: Double, y1: Double, y2: Double): Double = {
    val dx = x2 - x1
    val dy = y2 - y1
    dx * dx + dy * dy
  }

  private def contains(x: Double, y: Double, i: Int, j: Int, r2: Double): Int = {
    val dx = _dehashX(i) - x
    val dy = _dehashy(j) - y
    if (r2 > dx * dx + dy * dy) 1 else 0
  }

  override def query_point_count(x: Double, y: Double, r: Double): Int = {
    val center = _hashFunction(x, y)
    val intRX = _hashX(x + r) + 1 - center._1
    var intRY = _hashY(y + r) + 1 - center._2
    println("Query length = " + (3.14*(intRX.toDouble*intRX.toDouble+intRY.toDouble*intRY.toDouble)))
    val r2 = r * r
    var counter = 0
    var i = 1
    var j = 1
    counter += _query_bucket(center, i, j, x, y, r2) //Query center

    while (i <= intRX) { //Query x - axis
      counter += _query_bucket(center, -i, 0, x, y, r2)
      counter += _query_bucket(center, i, 0, x, y, r2)
      //      }
      i += 1
    }
    i = 1
    while (i <= intRY) {
      counter += _query_bucket(center, 0, j, x, y, r2)
      counter += _query_bucket(center, 0, -j, x, y, r2)
      //      }
      i += 1
    }
    i = 1
    while (i <= intRX) {
      val xSpread = _dehashX(i)
      intRY = _hashY(y + sqrt(r2 - (xSpread - x) * (xSpread - x))) + 2
      while (j <= intRY) {
        counter += _query_bucket(center, i, j, x, y, r2)
        counter += _query_bucket(center, -i, j, x, y, r2)
        counter += _query_bucket(center, i, -j, x, y, r2)
        counter += _query_bucket(center, -i, -j, x, y, r2)
        //        }
        j += 1
      }
      j = 1
      i += 1
    }
    counter
  }

  //  override def query_point_count2(x: Double, y: Double, r: Double): Int = {
  //    val center = _hashFunction(x, y)
  //    val intRX = _hashX(x + r) + 1 - center._1
  //    var intRY = _hashY(y + r) + 1 - center._2
  //    val r2 = r * r
  //    var counter = 0
  //    var i = 1
  //    var j = 1
  //    counter += _query_bucket(center,i,j, x, y, r2) //Query center
  //
  //    counter
  //  }

  override def query_points(pts: Iterator[((Int, Int), DoublePair)], r: Double): Iterator[((Int, Int), Index)] = {
    pts.map(pt => pt._1 -> query_point_count(pt._2._1, pt._2._2, r))
  }

  override def size: Int = sz

}

object MemGrid {

  val bucketFactor = 2
  def apply(data: IndexedSeq[DoublePair], bucketFactor: Int = bucketFactor): MemGrid = {
    val xHashPair = hashDehashPair(data, (l: DoublePair) => l._1, math.sqrt(data.size).toInt * bucketFactor)
    val yHashPair = hashDehashPair(data, (l: DoublePair) => l._2, math.sqrt(data.size).toInt * bucketFactor)
    //    val _hashX = equalHashing(data, (l: (Double, Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
    //    val _hashY = equalHashing(data, (l: (Double, Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
    val numBucs = math.sqrt(data.size).toInt * bucketFactor
    val grid: mutable.Map[Index, mutable.Map[Index, mutable.ArrayBuffer[Double]]] = mutable.Map()
    //    val grid = Array.fill(numBucs)(Array.fill(numBucs)(mutable.ArrayBuffer[Double]()))
    var rover = 0
    var xMin = Double.MaxValue
    var xMax = -Double.MaxValue
    var yMin = Double.MaxValue
    var yMax = -Double.MaxValue
    while (rover < data.size) {
      val elem = data(rover)
      val x = xHashPair._1(elem._1)
      val y = yHashPair._1(elem._2)
      if (!grid.contains(x)) grid(x) = mutable.Map()
      if (!grid(x).contains(y)) grid(x)(y) = mutable.ArrayBuffer()
      grid(x)(y) += elem._1
      grid(x)(y) += elem._2
      rover += 1
      if (elem._1 < xMin) xMin = elem._1
      if (elem._2 < yMin) yMin = elem._2
      if (elem._2 > yMax) yMax = elem._2
      if (elem._1 > xMax) xMax = elem._1
    }
    new MemGrid(grid, xHashPair, yHashPair, data.size, (xMin, xMax, yMin, yMax))
  }
}
