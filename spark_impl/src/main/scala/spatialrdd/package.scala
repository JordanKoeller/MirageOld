import org.apache.spark.rdd.RDD

package object spatialrdd {
  case class MinMax2D(var xMin: Double = Double.MaxValue, var yMin: Double = Double.MaxValue, var xMax: Double = -Double.MaxValue, var yMax: Double = -Double.MaxValue)
  case class MinMax(var min: Double = Double.MaxValue, var max: Double = -Double.MaxValue)

  type DoublePair = (Double, Double)
  type IntPair = (Int,Int)
  
  type HashFunc = Double => Int
  type Dehasher = Int => Double
  
  //  class IntPair(val x: Int, val y: Int) extends Serializable
  //  class DoublePair(val x: Double, val y: Double) extends Serializable

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
    val div = (minMax.max - minMax.min) / math.sqrt(buckets)
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
  
  def hashDehashPair(data: IndexedSeq[DoublePair],op:DoublePair => Double, buckets:Int):(HashFunc,Dehasher) = {
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
    val div = (minMax.max - minMax.min) / buckets.toInt
    val hash = (x: Double) => ((x - minMax.min) / div).toInt
    val dehash = (x: Int) => (x.toDouble*div + minMax.min)
    (hash,dehash)
  }

  def equalHashing2D(data: RDD[DoublePair], buckets: Int): DoublePair => (Int, Int) = {
    val minMax = data.aggregate(MinMax2D())((lastExtremes, elem) => {
      val x = elem._1
      val y = elem._2
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
    (pt: DoublePair) => (((pt._1 - minMax.xMin) / divX).toInt, ((pt._2 - minMax.yMin) / divY).toInt)
    //    (pt: DoublePair) =>
  }

  def equalHashing2D(data: IndexedSeq[DoublePair], buckets: Int): DoublePair => (Int, Int) = {
    val minMax = data.aggregate(MinMax2D())((lastExtremes, elem) => {
      val x = elem._1
      val y = elem._2
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
    (pt: DoublePair) => (((pt._1 - minMax.xMin) / divX).toInt, ((pt._2 - minMax.yMin) / divY).toInt)
  }

}
