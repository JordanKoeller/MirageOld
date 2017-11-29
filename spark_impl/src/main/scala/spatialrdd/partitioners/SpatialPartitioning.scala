package spatialrdd.partitioners

import org.apache.spark.Partitioner
import org.apache.spark.rdd.RDD
import scala.reflect.ClassTag

import spatialrdd.XYDoublePair

trait SpatialPartitioning extends Partitioner {

  type K = Double
  type V = Double

  def profileData(data: RDD[XYDoublePair]): RDD[(K, V)]

  def getPartitions(key: XYDoublePair, r: Double): Set[Int]

}