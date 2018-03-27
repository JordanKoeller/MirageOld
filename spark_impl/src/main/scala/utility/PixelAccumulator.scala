package utility

import org.apache.spark.util.AccumulatorV2
class PixelAccumulator(width: Int, height: Int) extends AccumulatorV2[(Int, Int, Int), Array[Int]] {

  type IN = (Int, Int, Int)
  type OUT = Array[Int]

  private val pixelGrid = Array.fill(width * height)(0)

  private var isEmpty = true

  def add(v: IN): Unit = {
    isEmpty = false
    pixelGrid(v._1 * width + v._2) +=  v._3
    //    pixelGrid(v._1)(v._2) += v._3
  }
  //   Takes the inputs and accumulates.

  def copy(): AccumulatorV2[IN, OUT] = {
    val ret = new PixelAccumulator(width, height)
    val curr = this.value
	for (i <- curr.indices) ret.add((i/width,i%width,curr(i)))
    ret
  }
  //		Creates a new copy of this accumulator.

  def isZero: Boolean = {
    isEmpty

  }
  //Returns if this accumulator is zero value or not.

  def merge(other: AccumulatorV2[IN, OUT]): Unit = {
      for (i <- other.value.indices) pixelGrid(i) += other.value(i)
  }
  //Merges another same-type accumulator into this one and update its state, i.e.

  def reset(): Unit = {
      for (i <- pixelGrid.indices) pixelGrid(i) = 0
//    var rover = 0
//    while (rover < width * height) {
//      val w = rover / width
//      val h = rover % width
//      this.add((w, h, 0))
//      rover += 1
//    }
    isEmpty = true
  }
  //Resets this accumulator, which is zero value.

  def value: OUT = {
    pixelGrid

  }

  def getGrid(): Array[Array[Int]] = {
    val ret = Array.fill(width, height)(0)
    for (rover <- pixelGrid.indices) ret(rover/width)(rover%width) = pixelGrid(rover)
    ret
  }
  //Defines the current value of this accumulator

}
