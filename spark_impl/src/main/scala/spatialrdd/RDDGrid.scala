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

class RDDGrid(data: RDD[(Double, Double)], partitioner: SpatialPartitioning) extends RDDGridProperty {
  private val rdd = _init(data, partitioner)

  def _init(data: RDD[(Double, Double)], partitioner: SpatialPartitioning) = {
    val rddProfiled = partitioner.profileData(data)
    val rddTraced = rddProfiled.partitionBy(partitioner)
    val glommed = rddTraced.glom()
    //    println (glommed.map(_.length).collect.mkString(","))
    val ret = glommed.map(arr => MemGrid(arr)).persist(StorageLevel.MEMORY_AND_DISK_SER)
    ret
  }

  def query_2(gen: GridGenerator, radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]] = {
    println("Broadcasting generator")
    val bgen = sc.broadcast(gen)
    val r = sc.broadcast(radius)
    println("Done. Now onto Querying")
    val queries = rdd.flatMap { grid =>
      gen.flatMap { qPt =>
        if (grid.intersects(qPt.x,qPt.y, r.value)) List(pixelConstructor(qPt.px, qPt.py, grid.query_point_count(qPt.x, qPt.y, r.value)))
        else List[PixelValue]()
      }
    }
<<<<<<< HEAD
    rdd.count()
    accumulator.getGrid()
*/
    
    val ret = Array.fill(pts.size,pts(1).size)(0)
    val retPairs = rdd.aggregate(Array[Long]())((counter,grid) => {
      val relevantQueryPts = broadcastedGroups.value(grid.partitionIndex)
      val newPts = relevantQueryPts.map{qPt =>
        val x = qPt._1._1 
        val y = qPt._1._2
        val num = grid.query_point_count(x, y, radius)
        val pos = (x.toLong << 16) + y.toInt
        (pos.toLong << 32) + num.toLong
      }
      counter ++ newPts
    }, (c1,c2) => c1 ++ c2)
    retPairs.foreach{elem =>
      ret((elem >>48).toInt)((elem << 48 >> 48).toInt) += (elem >> 32).toInt
=======

    val collected = queries.collect()
    println("Collected. Formatting Return")
    val ret = Array.fill(gen.xDim, gen.yDim)(0)
    collected.foreach { elem =>
      ret(elem.x)(elem.y) += elem.value
>>>>>>> 46e94f79aa28282b23f16fddafd60b11fc61e56f
    }
    ret
  }

//  def queryPoints(pts: Array[Array[(Double, Double)]], radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Index]] = {
//    val groupings = Array.fill(partitioner.numPartitions)(collection.mutable.ListBuffer[((Int, Int), (Double, Double))]())
//    println(groupings.size)
//    //    val accumulator = new PixelAccumulator(pts.size,pts(0).size)
//    //    sc.register(accumulator)
//    //    print("For looping")
//    for (i <- 0 until pts.size; j <- 0 until pts(0).size) {
//      println(i)
//      val pt = pts(i)(j)
//      val keys = partitioner.getPartitions(pt, radius)
//      keys.foreach { key =>
//        //        val adding = mkPair(i.toShort, j.toShort)
//        val adding = (i, j)
//        groupings(key) += adding -> pt
//      }
//    }
//    println("Done for looping. Now broadcasting")
//    val broadcastedGroups = sc.broadcast(groupings)
//    println("Done broadcasting")
//    /*    rdd.foreach{grid =>
//      val relevantQP = broadcastedGroups.value(grid.partitionIndex)
//      relevantQP.foreach{qp =>
//        val count = grid.query_point_count(qp._2._1, qp._2._1, radius)
//        accumulator add (qp._1._1,qp._1._2,count)
//      }
//    }
//    rdd.count()
//    accumulator.getGrid()
//*/
//    println("Now querying the thing")
//    val ret = Array.fill(pts.size, pts(1).size)(0)
//    //    val retPairs = rdd.aggregate(Array[((Int,Int),Int)]())((counter,grid) => {
//    //      val relevantQueryPts = broadcastedGroups.value(grid.partitionIndex)
//    //      val newPts = relevantQueryPts.map{qPt =>
//    ////        pixelConstructor(qPt._1._1,qPt._1._2,grid.query_point_count(qPt._2._1, qPt._2._2, radius))
//    //        ((qPt._1._1,qPt._1._2),grid.query_point_count(qPt._2._1, qPt._2._2, radius))
//    //      }
//    //      counter ++ newPts
//    //    }, (c1,c2) => c1 ++ c2)
//    val retPairs = rdd.flatMap { grid =>
//      val qPoints = broadcastedGroups.value(grid.partitionIndex)
//      qPoints.map { qPt =>
//        pixelConstructor(qPt._1._1, qPt._1._2, grid.query_point_count(qPt._2._1, qPt._2._2, radius))
//      }
//    }
//    broadcastedGroups.destroy()
//
//    retPairs.collect().foreach { elem =>
//      ret(elem.x)(elem.y) += elem.value
//    }
//    ret
//  }

  def count: Long = rdd.count()

}
