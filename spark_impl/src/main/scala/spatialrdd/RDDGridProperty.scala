package spatialrdd

import org.apache.spark.SparkContext

import utility.DoublePair
import utility.Index
trait RDDGridProperty {
//  def queryPoints(pts: Array[Array[DoublePair]], radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Index]]

  def count: Long
<<<<<<< HEAD
  def queryPoints(gen: GridGenerator, radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]]

}
=======
  def query_2(gen: GridGenerator, radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]]
  def destroy():Unit
  
  def printSuccess:Unit
}
>>>>>>> f8a13efb45397f21e9f0d32537918b73033791f4
