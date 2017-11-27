package data_structures
import collection.mutable

case class XYPair(val x: Double, val y: Double)
class SpatialGrid[T <: XYPair](data: IndexedSeq[T], bucketFactor: Int = 1) {
  private val _buckets: mutable.HashMap[Int, Map[Int, mutable.ArrayBuffer[Int]]] = collection.mutable.HashMap()
  private sealed case class MinMax(var xMin: Double = Double.MaxValue, var yMin: Double = Double.MaxValue, var xMax: Double = Double.MinValue, var yMax: Double = Double.MinValue)
  private sealed case class XYIntPair(val x: Int, val y: Int)

  private val Array(xMin, yMin, xDiv, yDiv) = _profileData()
  for (i <- 0 until data.size) _insert_pt(i)

  private def _hashX(x: Double): Int = {
    ((x - xMin) / xDiv).toInt
  }

  private def _hashY(y: Double): Int = {
    ((y - yMin) / yDiv).toInt
  }

  private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
    val x = _hashX(xx)
    val y = _hashY(yy)
    XYIntPair(x, y)
  }

  private def _profileData(): Array[Double] = {
    val minMax = data.foldLeft(MinMax()) { (lastExtremes, elem) =>
      val x = elem.x
      val y = elem.y
      if (x > lastExtremes.xMax) {
        lastExtremes.xMax = x
      }
      if (y > lastExtremes.yMax) {
        lastExtremes.yMax = y
      }
      if (x < lastExtremes.xMin) {
        lastExtremes.xMin = x
      }
      if (y < lastExtremes.yMin) {
        lastExtremes.yMin = y
      }
      lastExtremes
    }
    val numPts = bucketFactor * data.size.toDouble

    val xDiv = (minMax.xMax - minMax.xMin) / numPts
    val yDiv = (minMax.yMax - minMax.yMin) / numPts
    Array(minMax.xMin, minMax.yMin, xDiv, yDiv)
  }

  private def _insert_pt(index: Int): Unit = {
    val coords = _hashFunction(data(index).x, data(index).y)
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
}

object SpatialGrid {

}