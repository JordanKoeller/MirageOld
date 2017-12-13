package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import spatialrdd.partitioners.SpatialPartitioning
// import spatialrdd.SpatialData
import org.apache.spark.storage.StorageLevel

class RDDGrid(data: RDD[XYDoublePair], partitioner: SpatialPartitioning) extends RDDGridProperty {
  private val rdd = _init(data,partitioner) 
  def _init(data:RDD[XYDoublePair], partitioner:SpatialPartitioning) = {
    val rddProfiled = partitioner.profileData(data)
    val rddTraced = rddProfiled.partitionBy(partitioner)
    val ret = rddTraced.glom().mapPartitions(arrr => arrr.map(arr => VectorGrid(arr))).persist(StorageLevel.MEMORY_AND_DISK)
    println("Put on " + rddTraced.getNumPartitions + " partitions")
    ret
  }

  def queryPoints(pts: Array[Array[XYDoublePair]], radius: Double, sc: SparkContext,verbose:Boolean = false): Array[Array[Int]] = {
    val groupings = Array.fill(partitioner.numPartitions)(collection.mutable.ListBuffer[(XYIntPair, XYDoublePair)]())
    var counter = 0
    for (i <- 0 until pts.size; j <- 0 until pts(0).size) {
      val pt = pts(i)(j)
      val keys = partitioner.getPartitions(pt, radius)
      keys.foreach{key =>
        val adding = new XYIntPair(i,j)
        groupings(key) += adding -> pt
      }
    }
    println("Failed to key in " + counter + " query points")
    val broadcastedGroups = sc.broadcast(groupings)
    val ret = Array.fill(pts.size, pts(0).size)(0)
    var counter2 = 0
    println("Now querying the grids")
    val countRDD = rdd.mapPartitionsWithIndex((ind, gridInIterator) => {
      val grid = gridInIterator.next()
      broadcastedGroups.value(ind).map{ elem =>
        elem._1 -> grid.query_point_count(elem._2.x, elem._2.y, radius)
      }.iterator
    }, true)
    countRDD.collect().foreach { elem => ret(elem._1.x)(elem._1.y) += elem._2 }
    println("DONE")
    ret


  }

  def count:Long = rdd.count()

}
