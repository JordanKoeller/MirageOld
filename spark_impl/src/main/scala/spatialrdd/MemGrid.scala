package spatialrdd
import scala.collection.mutable

import math.sqrt

//class MemGrid(grid: Array[Array[mutable.ArrayBuffer[Double]]], _hashX: Double => Int, _hashY: Double => Int, sz: Int, val partitionIndex: Int) extends SpatialData {
class MemGrid(grid: mutable.Map[Int, mutable.Map[Int, mutable.ArrayBuffer[Double]]], hashXPair: (HashFunc, Dehasher), hashYPair: (HashFunc, Dehasher), sz: Int, val partitionIndex: Int) extends SpatialData {

  private def _hashX = hashXPair._1

  private def _hashY = hashYPair._1

  private def _dehashX = hashXPair._2

  private def _dehashy = hashYPair._2

  private def _hashFunction(xx: Double, yy: Double): (Int, Int) = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    (x, y)
  }

  private def _query_bucket(i: Int, j: Int, x: Double, y: Double, r2: Double): Int = {
    if (grid.contains(i) && grid(i).contains(j)) {
      if (grid(i)(j).size > 0) {
        var counter = 0
        var ind = 0
        var dx = 0.0
        var dy = 0.0
        while (ind < grid(i)(j).size) {
          dx = grid(i)(j)(ind) - x
          dy = grid(i)(j)(ind + 1) - y
          if (r2 >= dx * dx + dy * dy) counter += 1
          ind += 2
        }
        counter
      } else 0
    } else 0
  }

  private def _fetch_bucket(i: Int, j: Int): Int = {
    if (grid.contains(i) && grid(i).contains(j)) {
      grid(i)(j).size / 2
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
    val center = _hashFunction(x, y)
    val intRX = _hashX(x + r) + 1 - center._1
    var intRY = _hashY(y + r) + 1 - center._2
    val r2 = r * r
    var counter = 0
    var i = 1
    var j = 1
    counter += _query_bucket(center._1, center._2, x, y, r2) //Query center

    while (i <= intRX) { //Query x - axis
//      if (i < (intRX - 2)) {
//        counter += _fetch_bucket(center._1 + i, center._2)
//        counter += _fetch_bucket(center._1 - i, center._2)
//      } else {
        counter += _query_bucket(center._1 + i, center._2, x, y, r2)
        counter += _query_bucket(center._1 - i, center._2, x, y, r2)
//      }
      i += 1
    }
    i = 1
    while (i <= intRY) {
//      if (i < (intRY - 2)) {
//        counter += _fetch_bucket(center._1, center._2 + i)
//        counter += _fetch_bucket(center._1, center._2 - i)
//      } else {
        counter += _query_bucket(center._1, center._2 + i, x, y, r2)
        counter += _query_bucket(center._1, center._2 - i, x, y, r2)
//      }
      i += 1
    }
    i = 1
    while (i <= intRX) {
      val xSpread = _dehashX(i)
      intRY = _hashY(y + sqrt(r2 - (xSpread - x) * (xSpread - x))) + 2
      while (j <= intRY) {
//        if (i < (intRX - 2) && j < (intRY - 2)) {
//          counter += _fetch_bucket(center._1 + i, center._2 + j)
//          counter += _fetch_bucket(center._1 + i, center._2 - j)
//          counter += _fetch_bucket(center._1 - i, center._2 + j)
//          counter += _fetch_bucket(center._1 - i, center._2 - j)
//        } else {

          counter += _query_bucket(center._1 + i, center._2 + j, x, y, r2)
          counter += _query_bucket(center._1 + i, center._2 - j, x, y, r2)
          counter += _query_bucket(center._1 - i, center._2 + j, x, y, r2)
          counter += _query_bucket(center._1 - i, center._2 - j, x, y, r2)
//        }
        j += 1
      }
      j = 1
      i += 1
    }
    counter
  }

  override def query_points(pts: Iterator[((Int, Int), (Double, Double))], r: Double): Iterator[((Int, Int), Int)] = {
    pts.map(pt => pt._1 -> query_point_count(pt._2._1, pt._2._2, r))
  }

  override def size: Int = sz

}

object MemGrid {

  val bucketFactor = 4
  def apply(data: IndexedSeq[(Double, Double)], partitionIndex: Int, bucketFactor: Int = bucketFactor): MemGrid = {
    val xHashPair = hashDehashPair(data, (l: (Double, Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
    val yHashPair = hashDehashPair(data, (l: (Double, Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
    //    val _hashX = equalHashing(data, (l: (Double, Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
    //    val _hashY = equalHashing(data, (l: (Double, Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
    val numBucs = math.sqrt(data.size).toInt * bucketFactor
    val grid: mutable.Map[Int, mutable.Map[Int, mutable.ArrayBuffer[Double]]] = mutable.Map()
    //    val grid = Array.fill(numBucs)(Array.fill(numBucs)(mutable.ArrayBuffer[Double]()))
    var rover = 0
    while (rover < data.size) {
      val elem = data(rover)
      val x = xHashPair._1(elem._1)
      val y = yHashPair._1(elem._2)
      if (!grid.contains(x)) grid(x) = mutable.Map()
      if (!grid(x).contains(y)) grid(x)(y) = mutable.ArrayBuffer()
      grid(x)(y) += elem._1
      grid(x)(y) += elem._2
      rover += 1
    }
    new MemGrid(grid, xHashPair, yHashPair, data.size, partitionIndex)
  }
}
