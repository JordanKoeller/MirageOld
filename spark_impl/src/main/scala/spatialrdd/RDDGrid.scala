package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import spatialrdd.partitioners.SpatialPartitioning
import spatialrdd.partitioners.ColumnPartitioner
import spatialrdd.partitioners.BalancedColumnPartitioner
// import spatialrdd.SpatialData
import org.apache.spark.storage.StorageLevel

import org.apache.spark.RangePartitioner

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

object RDDGrid {
    // val conf = new SparkConf().setAppName("RDDGrid Test").setMaster("local[*]")
    // val sc = new SparkContext(conf)
    // sc.setLogLevel("WARN")
  // def Test(np:Int):Unit =  {

  //   val h = 1000
  //   val w = 1000
  //   val data = sc.range(0,h*w,1,np)
  //   val gridData = data.map(elem => new XYDoublePair(math.sin((elem%w).toDouble),math.sin((elem/w).toDouble)))
  //   val data2 = gridData.sortBy(_.x)
  //   // val partitioner = new ColumnPartitioner()
  //   val partitioner = new BalancedColumnPartitioner()

  //   val rddgrid = new RDDGrid(data2,partitioner)
  //   val radius = 0.1
  //   val queryPts = Array.fill(5)(Array.fill(5)(new XYDoublePair(50.0,60.0)))
  //   for (i <- 0 until 5;j <- 0 until 5) queryPts(i)(j) = new XYDoublePair(i.toDouble/math.Pi,j.toDouble/math.Pi)
  //   val ret = rddgrid.queryPoints(queryPts,radius,sc,true)
  //   ret.map(_.mkString(",")) foreach println
  // }

  // def RangeTest() = {
  //   val conf = new SparkConf().setAppName("RDDGrid Test").setMaster("local[*]")
  //   val sc = new SparkContext(conf)
  //   sc.setLogLevel("WARN")
  //   val data2 = sc.range(0,100,1,10)
  //   val data = data2.map(i => (math.sin(math.Pi*i*2.0/100.0),i))
  //   val partitioner = new RangePartitioner(10,data)
  //   data.partitionBy(partitioner).glom().collect.foreach(i =>println(i.map(_._1).mkString(",")))
  // }

// RangeTest()
  // Test(1)
  // Test(100)

  // sc.stop()
}