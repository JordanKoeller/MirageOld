package utility

import org.apache.spark.util.AccumulatorV2
import java.util.concurrent.atomic.AtomicIntegerArray
class PixelAccumulator(width: Int, height: Int) extends AccumulatorV2[(Int, Int, Int), AtomicIntegerArray] {

  type IN = (Int, Int, Int)
  type OUT = AtomicIntegerArray

  private val pixelGrid = new AtomicIntegerArray(width * height)

  private var isEmpty = true

  def add(v: IN): Unit = {
    isEmpty = false
    pixelGrid.getAndAdd(v._1 * width + v._2, v._3)
    //    pixelGrid(v._1)(v._2) += v._3
  }
  //   Takes the inputs and accumulates.

  def copy(): AccumulatorV2[IN, OUT] = {
    val ret = new PixelAccumulator(width, height)
    val curr = this.value
    if (!isEmpty) {
      var rover = 0
      while (rover < width * height) {
        val w = rover / width
        val h = rover % width
        ret.add((w, h, pixelGrid.get(rover)))
        rover += 1
      }
    }
    ret
  }
  //		Creates a new copy of this accumulator.

  def isZero: Boolean = {
    isEmpty

  }
  //Returns if this accumulator is zero value or not.

  def merge(other: AccumulatorV2[IN, OUT]): Unit = {
    if (!other.isZero) {
      val otherV = other.value
      var rover = 0
      while (rover < width * height) {
        val w = rover / width
        val h = rover % width
        this.add((w, h, otherV.get(rover)))
        rover += 1
      }
    }
  }
  //Merges another same-type accumulator into this one and update its state, i.e.

  def reset(): Unit = {
    var rover = 0
    while (rover < width * height) {
      val w = rover / width
      val h = rover % width
      this.add((w, h, 0))
      rover += 1
    }
  }
  //Resets this accumulator, which is zero value.

  def value: OUT = {
    pixelGrid

  }

  def getGrid(): Array[Array[Int]] = {
    val ret = Array.fill(width, height)(0)
    var rover = 0
    while (rover < width * height) {
      val w = rover / width
      val h = rover % width
      ret(w)(h) = pixelGrid.get(rover)
      rover += 1
    }
    ret
  }
  //Defines the current value of this accumulator

}