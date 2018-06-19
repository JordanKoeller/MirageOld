package utility

import org.apache.spark.util.AccumulatorV2
import utility._

class PixelAccumulator(h: Int, w: Int) extends AccumulatorV2[Long, Array[Array[Int]]] {
  private val arr: Array[Array[Int]] = Array.fill(w, h)(0)
  private var iszer: Boolean = true
  def add(v: Long): Unit = {
    val tmp = pixelConstructor(v)
    synchronized {
      arr(tmp.x)(tmp.y) += tmp.value
      iszer = false
    }
  }

  def isZero: Boolean = iszer

  def copy(): PixelAccumulator = {
    val cp = new PixelAccumulator(h, w)
    for (i <- 0 until w) {
      for (j <- 0 until h) {
        val tmp = pixelLongConstructor(i, j, arr(i)(j))
        cp.add(tmp)
      }
    }
    cp
  }

  def merge(other: AccumulatorV2[Long, Array[Array[Int]]]): Unit = {
    for (i <- 0 until w) {
      for (j <- 0 until h) {
        val tmp = pixelLongConstructor(i, j, other.value(i)(j))
        add(tmp)
      }
    }
  }

  def reset(): Unit = {
    synchronized {
      for (i <- 0 until w) {
        for (j <- 0 until h) {
          val tmp = pixelLongConstructor(i, j, -arr(i)(j))
          add(tmp)
        }
      }
      iszer = true
    }
  }

  def value: Array[Array[Int]] = arr

}
