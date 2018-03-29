package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import spatialrdd.partitioners.SpatialPartitioning
import spatialrdd.partitioners.BalancedColumnPartitioner
// import spatialrdd.SpatialData
import org.apache.spark.storage.StorageLevel

import org.apache.spark.RangePartitioner
import utility.PixelAccumulator
import utility.IndexPair
import utility.DoublePair
import utility.mkPair
import utility.Index
import utility.PixelValue
import utility.pixelConstructor

class RDDGrid(data: RDD[(Double,Double)], partitioner: SpatialPartitioning) extends RDDGridProperty {
  private val rdd = _init(data, partitioner)


  def _init(data: RDD[(Double,Double)], partitioner: SpatialPartitioning) = {
    val rddProfiled = partitioner.profileData(data)
    val rddTraced = rddProfiled.partitionBy(partitioner)
    val glommed = rddTraced.glom()
//    println (glommed.map(_.length).collect.mkString(","))
    val zipped = glommed.zipWithIndex()
    val ret = zipped.map(arr => MemGrid(arr._1,partitionIndex = arr._2.toInt)).persist(StorageLevel.MEMORY_ONLY_SER)
    ret
  }







  def queryPoints(pts: Array[Array[DoublePair]], radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Index]] = {
    val groupings = Array.fill(partitioner.numPartitions)(collection.mutable.ArrayBuffer[(IndexPair, DoublePair)]())
//    val accumulator = new PixelAccumulator(pts.size,pts(0).size)
//    sc.register(accumulator)
    for (i <- 0 until pts.size; j <- 0 until pts(0).size) {
      val pt = pts(i)(j)
      val keys = partitioner.getPartitions(pt, radius)
      keys.foreach { key =>
        val adding = mkPair(i.toShort, j.toShort)
        groupings(key) += adding -> pt
      }
    }
    val broadcastedGroups = sc.broadcast(groupings)
/*    rdd.foreach{grid =>
      val relevantQP = broadcastedGroups.value(grid.partitionIndex)
      relevantQP.foreach{qp =>
        val count = grid.query_point_count(qp._2._1, qp._2._1, radius)
        accumulator add (qp._1._1,qp._1._2,count)
      }
    }
    rdd.count()
    accumulator.getGrid()
*/
    
    val ret = Array.fill(pts.size,pts(1).size)(0)
    val retPairs = rdd.aggregate(Set[PixelValue]())((counter,grid) => {
      val relevantQueryPts = broadcastedGroups.value(grid.partitionIndex)
      val newPts = relevantQueryPts.map{qPt =>
        pixelConstructor(qPt._1._1,qPt._1._2,grid.query_point_count(qPt._2._1, qPt._2._2, radius))
      }
      counter ++ newPts
    }, (c1,c2) => c1 ++ c2)
    retPairs.foreach{elem => 
      ret(elem.x)(elem.y) += elem.value
    }
    ret
  }

  def count: Long = rdd.count()

}
