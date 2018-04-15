package spatialrdd

import org.apache.spark.SparkContext

import utility.DoublePair
import utility.Index
trait RDDGridProperty {
//  def queryPoints(pts: Array[Array[DoublePair]], radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Index]]

  def count: Long
  def query_2(gen: GridGenerator, radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]]
  def destroy():Unit
  
  def printSuccess:Unit
}
