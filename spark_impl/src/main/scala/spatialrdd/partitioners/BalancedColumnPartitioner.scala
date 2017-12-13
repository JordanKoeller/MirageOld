package spatialrdd.partitioners

import org.apache.spark.rdd.RDD
import org.apache.spark.RangePartitioner
import spatialrdd.XYDoublePair
import spatialrdd.equalHashing
import spatialrdd.MinMax

class BalancedColumnPartitioner extends SpatialPartitioning {
  private var _numPartitions = 1
  private var _ranger:RangePartitioner[Double,Double] = _


  def getPartition(key: Any): Int = {
    _ranger.getPartition(key)
  }

  def getPartitions(key: XYDoublePair, r: Double): Set[Int] = {
    Set(getPartition(key.x - r), getPartition(key.x), getPartition(key.x + r))

  }

  def numPartitions: Int = {
    _numPartitions
  }

  override def profileData(data: RDD[XYDoublePair]): RDD[(Double, Double)] = {
    _numPartitions = 16
    println("Putting on " + _numPartitions)
    val ret = data.mapPartitions(elemIter => elemIter.map(elem => (elem.x, elem.y)),true) 
    _ranger = new RangePartitioner(numPartitions, ret)
    ret
  }
}
