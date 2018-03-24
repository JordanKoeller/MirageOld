package spatialrdd.partitioners

import org.apache.spark.rdd.RDD
import org.apache.spark.RangePartitioner
import spatialrdd.equalHashing
import spatialrdd.MinMax

class BalancedColumnPartitioner extends SpatialPartitioning {
  private var _numPartitions = 1
  private var _ranger:RangePartitioner[Double,Double] = _


  def getPartition(key: Any): Int = {
    _ranger.getPartition(key)
  }

  def getPartitions(key: (Double,Double), r: Double): Set[Int] = {
    (for (i <- getPartition(key._1 - r) to getPartition(key._1+r)) yield i).toSet


  }

  def numPartitions: Int = {
    _numPartitions
  }

  override def profileData(data: RDD[(Double,Double)]): RDD[(Double, Double)] = {
    _numPartitions = data.getNumPartitions
    println("Found and setting number of partitions as " + _numPartitions)
//    val shuffled = data.repartition(_numPartitions)
    val ret = data.mapPartitions(elemIter => elemIter.map(elem => (elem._1, elem._2)),true) 
    _ranger = new RangePartitioner(_numPartitions, ret)
    ret
  }
}
