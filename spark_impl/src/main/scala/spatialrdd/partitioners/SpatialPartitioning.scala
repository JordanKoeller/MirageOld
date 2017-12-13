package spatialrdd.partitioners

import org.apache.spark.Partitioner
import org.apache.spark.rdd.RDD
import scala.reflect.ClassTag

import spatialrdd.XYDoublePair

trait SpatialPartitioning extends Partitioner {

  def profileData(data: RDD[XYDoublePair]):RDD[(Double,Double)]

  def getPartitions(key: XYDoublePair, r: Double): Set[Int]

}
