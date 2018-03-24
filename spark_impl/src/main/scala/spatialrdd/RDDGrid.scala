package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import spatialrdd.partitioners.SpatialPartitioning
import spatialrdd.partitioners.BalancedColumnPartitioner
// import spatialrdd.SpatialData
import org.apache.spark.storage.StorageLevel

import org.apache.spark.RangePartitioner

class RDDGrid(data: RDD[(Double,Double)], partitioner: SpatialPartitioning) extends RDDGridProperty {
  private val rdd = _init(data, partitioner)


  def _init(data: RDD[(Double,Double)], partitioner: SpatialPartitioning) = {
    val rddProfiled = partitioner.profileData(data)
//    va rddTraced = rddProfiled.partitionBy(partitioner)
    val ret = rddProfiled.mapPartitionsWithIndex((ind,arrr) => Iterator(MemGrid(arrr.toIndexedSeq,partitionIndex = ind))).persist(StorageLevel.MEMORY_ONLY)
    ret
  }







  def queryPoints(pts: Array[Array[(Double,Double)]], radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]] = {
    val groupings = Array.fill(partitioner.numPartitions)(collection.mutable.ListBuffer[(XYIntPair, (Double,Double))]())
    var counter = 0
    val ret = Array.fill(pts.size, pts(0).size)(0)
    for (i <- 0 until pts.size; j <- 0 until pts(0).size) {
      val pt = pts(i)(j)
      val keys = partitioner.getPartitions(pt, radius)
      keys.foreach { key =>
        val adding = new XYIntPair(i, j)
        groupings(key) += adding -> pt
      }
    }
    val broadcastedGroups = sc.broadcast(groupings)
    val retPairs = rdd.aggregate(new Array[(XYIntPair,Int)](0))((counter,grid) => {
      val relevantQueryPts = broadcastedGroups.value(grid.partitionIndex)
      val newPts = relevantQueryPts.map{qPt =>
        (new XYIntPair(qPt._1.x,qPt._1.y),grid.query_point_count(qPt._2._1, qPt._2._2, radius))
      }
      counter ++ newPts
    }, (c1,c2) => c1 ++ c2)
    retPairs.foreach{elem => 
      val coord = elem._1
      val value = elem._2
      ret(coord.x)(coord.y) += value
    }
    ret
  }

  def count: Long = rdd.count()

}
