import org.apache.spark.rdd.RDD

package object spatialrdd {
  sealed case class XYPair[T](val x: T, val y: T)
  case class MinMax2D(var xMin: Double = Double.MaxValue, var yMin: Double = Double.MaxValue, var xMax: Double = Double.MinValue, var yMax: Double = Double.MinValue)
  case class MinMax(var min: Double = Double.MaxValue, var max: Double = Double.MinValue)
  class XYIntPair(override val x: Int, override val y: Int) extends XYPair[Int](x, y)
  class XYDoublePair(override val x: Double, override val y: Double) extends XYPair[Double](x, y)

  def equalHashing[T](data: IndexedSeq[T], op: T => Double, buckets: Int): Double => Int = {
    val minMax = data.aggregate(MinMax())((lastExtremes, elem2) => {
      val elem = op(elem2)
      if (elem > lastExtremes.max) lastExtremes.max = elem
      if (elem < lastExtremes.min) lastExtremes.min = elem
      lastExtremes
    }, (mm1, mm2) => {
      val ret = MinMax()
      if (mm1.min < mm2.min) ret.min = mm1.min else ret.min = mm2.min
      if (mm1.max > mm2.max) ret.max = mm1.max else ret.max = mm2.max
      ret
    })
    val div = (minMax.max - minMax.min) / buckets.toDouble
    (x: Double) => ((x - minMax.min) / div).toInt
  }

  def equalHashing[T](data: RDD[T], op: T => Double, buckets: Int): Double => Int = {
    val minMax = data.aggregate(MinMax())((lastExtremes, elem2) => {
      val elem = op(elem2)
      if (elem > lastExtremes.max) lastExtremes.max = elem
      if (elem < lastExtremes.min) lastExtremes.min = elem
      lastExtremes
    }, (mm1, mm2) => {
      val ret = MinMax()
      if (mm1.min < mm2.min) ret.min = mm1.min else ret.min = mm2.min
      if (mm1.max > mm2.max) ret.max = mm1.max else ret.max = mm2.max
      ret
    })
    val div = (minMax.max - minMax.min) / buckets.toDouble
    (x: Double) => ((x - minMax.min) / div).toInt
  }

  def equalHashing2D[T <: XYDoublePair](data: RDD[T], buckets: Int): XYDoublePair => XYIntPair = {
    val minMax = data.aggregate(MinMax2D())((lastExtremes, elem) => {
      val x = elem.x
      val y = elem.y
      if (x > lastExtremes.xMax) lastExtremes.xMax = x
      if (y > lastExtremes.yMax) lastExtremes.yMax = y
      if (x < lastExtremes.xMin) lastExtremes.xMin = x
      if (y < lastExtremes.yMin) lastExtremes.yMin = y
      lastExtremes
    }, (mm1, mm2) => {
      val ret = MinMax2D()
      if (mm1.xMin < mm2.xMin) ret.xMin = mm1.xMin else ret.xMin = mm2.xMin
      if (mm1.xMax > mm2.xMax) ret.xMax = mm1.xMax else ret.xMax = mm2.xMax
      if (mm1.yMin < mm2.yMin) ret.yMin = mm1.yMin else ret.yMin = mm2.yMin
      if (mm1.yMax > mm2.yMax) ret.yMax = mm1.yMax else ret.yMax = mm2.yMax
      ret
    })
    val divX = (minMax.xMax - minMax.xMin) / buckets.toDouble
    val divY = (minMax.yMax - minMax.yMin) / buckets.toDouble
    (pt: XYDoublePair) => new XYIntPair(((pt.x - minMax.xMin) / divX).toInt, ((pt.y - minMax.yMin) / divY).toInt)
  }

  def equalHashing2D[T <: XYDoublePair](data: IndexedSeq[T], buckets: Int): XYDoublePair => XYIntPair = {
    val minMax = data.aggregate(MinMax2D())((lastExtremes, elem) => {
      val x = elem.x
      val y = elem.y
      if (x > lastExtremes.xMax) lastExtremes.xMax = x
      if (y > lastExtremes.yMax) lastExtremes.yMax = y
      if (x < lastExtremes.xMin) lastExtremes.xMin = x
      if (y < lastExtremes.yMin) lastExtremes.yMin = y
      lastExtremes
    }, (mm1, mm2) => {
      val ret = MinMax2D()
      if (mm1.xMin < mm2.xMin) ret.xMin = mm1.xMin else ret.xMin = mm2.xMin
      if (mm1.xMax > mm2.xMax) ret.xMax = mm1.xMax else ret.xMax = mm2.xMax
      if (mm1.yMin < mm2.yMin) ret.yMin = mm1.yMin else ret.yMin = mm2.yMin
      if (mm1.yMax > mm2.yMax) ret.yMax = mm1.yMax else ret.yMax = mm2.yMax
      ret
    })
    val divX = (minMax.xMax - minMax.xMin) / buckets.toDouble
    val divY = (minMax.yMax - minMax.yMin) / buckets.toDouble
    (pt: XYDoublePair) => new XYIntPair(((pt.x - minMax.xMin) / divX).toInt, ((pt.y - minMax.yMin) / divY).toInt)
  }

}
