package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import spatialrdd.partitioners.SpatialPartitioning

class RDDGrid(data: RDD[XYDoublePair], partitioner: SpatialPartitioning) {
  private val rdd = partitioner.profileData(data).partitionBy(partitioner).glom().map(arr => SpatialGrid(arr)).cache()

  def queryPoints(pts: Array[Array[XYDoublePair]], radius: Double, sc: SparkContext): Array[Array[Double]] = {
    val groupings = collection.mutable.Map[Int, List[(XYIntPair, XYDoublePair)]]()
    for (i <- 0 until pts.size; j <- 0 until pts(i).size) {
      val keys = partitioner.getPartitions(pts(i)(j), radius)
      keys.foreach { key =>
        groupings(key) ::= new XYIntPair(i, j) -> pts(i)(j)
      }
    }
    val broadcastedGroups = sc.broadcast(groupings)
    val ret = Array.fill(pts.size, pts(0).size)(0.0)
    val countRDD = rdd.mapPartitionsWithIndex((ind, gridInIterator) => {
      val grid = gridInIterator.next()
      broadcastedGroups.value(ind).map { elem =>
        elem._1 -> grid.query_point_count(elem._2.x, elem._2.y, radius)
      }.iterator
    }, true)
    countRDD.collect().foreach { elem => ret(elem._1.x)(elem._1.y) += elem._2 }
    ret
  }

}