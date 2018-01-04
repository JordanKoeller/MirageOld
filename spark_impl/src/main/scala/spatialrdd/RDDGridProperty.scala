package spatialrdd

import org.apache.spark.SparkContext

trait RDDGridProperty {
    def queryPoints(pts: Array[Array[XYDoublePair]], radius: Double, sc: SparkContext,verbose:Boolean = false): Array[Array[Int]]
    
    def count:Long


}