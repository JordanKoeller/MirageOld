package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import spatialrdd.partitioners.SpatialPartitioning

class RDDGrid(data: RDD[XYDoublePair], partitioner: SpatialPartitioning) {
  private val rdd = _init(data,partitioner) 
  def _init(data:RDD[XYDoublePair], partitioner:SpatialPartitioning) = {
    val rddProfiled = partitioner.profileData(data)
    val rddTraced = rddProfiled.partitionBy(partitioner)
    // rddTraced.collect()
    val ret = rddTraced.glom().mapPartitions(arrr => arrr.map(arr => OptGrid(arr))).cache()
    ret
  }

  def queryPoints(pts: Array[Array[XYDoublePair]], radius: Double, sc: SparkContext): Array[Array[Double]] = {
    val groupings = Array.fill(partitioner.numPartitions)(collection.mutable.ListBuffer[(XYIntPair, XYDoublePair)]())
    var counter = 0
    for (i <- 0 until pts.size; j <- 0 until pts(0).size) {
      val pt = pts(i)(j)
      val keys = partitioner.getPartitions(pt, radius)
      keys.foreach{key =>
        if (key < 256) groupings(key) += new XYIntPair(i, j) -> pts(i)(j)
        else {
          println("FOUND ERROR KEY "+key)
          counter += 1
        }
      }
    }
    println("Failed to key in " + counter + " query points")
    val broadcastedGroups = sc.broadcast(groupings)
    val ret = Array.fill(pts.size, pts(0).size)(0.0)
    var counter2 = 0
    val countRDD = rdd.mapPartitionsWithIndex((ind, gridInIterator) => {
      val grid = gridInIterator.next()
      broadcastedGroups.value(ind).map { elem =>
        print("On iteration number "+counter2)
        counter += 1
        elem._1 -> grid.query_point_count(elem._2.x, elem._2.y, radius)
      }.iterator
    }, true)
    countRDD.collect().foreach { elem => ret(elem._1.x)(elem._1.y) += elem._2 }
    println("DONE")
    ret
  }

  def count:Long = rdd.count()

}
