package spatialrdd

import org.apache.spark.SparkContext
import utility.Index
import utility.DoublePair
trait RDDGridProperty {
    def queryPoints(pts: Array[Array[DoublePair]], radius: Double, sc: SparkContext,verbose:Boolean = false): Array[Array[Index]]
    
    def count:Long


}