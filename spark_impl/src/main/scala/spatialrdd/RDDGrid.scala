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
import spatialrdd.partitioners.BalancedColumnPartitioner

class RDDGrid(data: RDD[(Double, Double)], partitioner: SpatialPartitioning = new BalancedColumnPartitioner, nodeStructure: IndexedSeq[(Double, Double)] => SpatialData = MemGrid.apply) extends RDDGridProperty {
  private val rdd = _init(data, partitioner)

  def _init(data: RDD[(Double, Double)], partitioner: SpatialPartitioning) = {
    val rddProfiled = partitioner.profileData(data)
    val rddTraced = rddProfiled.partitionBy(partitioner)
    val glommed = rddTraced.glom()
    //    println (glommed.map(_.length).collect.mkString(","))
    val ret = glommed.map(arr => nodeStructure(arr)).persist(StorageLevel.MEMORY_ONLY)
    ret
  }

  def queryPointsFromGen(gen: GridGenerator, radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]] = {
    println("Broadcasting generator")
    val bgen = sc.broadcast(gen)
    val r = sc.broadcast(radius)
    val queries = rdd.flatMap { grid =>
      gen.flatMap { qPt =>
        if (grid.intersects(qPt.x, qPt.y, r.value)) {
          val num = grid.query_point_count(qPt.x, qPt.y, r.value)
          if (num != 0) pixelConstructor(qPt.px, qPt.py, num) :: Nil else Nil
        } else Nil
      }
    }

    val collected = queries.collect()
    val ret = Array.fill(gen.xDim, gen.yDim)(0)
    collected.foreach { elem =>
      ret(elem.x)(elem.y) += elem.value
    }
    ret
  }
  def queryPoints(pts: Array[Array[DoublePair]], radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Index]] = {
    println("Size = " + pts.size)
    val r = sc.broadcast(radius)
    val queryPts = sc.broadcast(pts)
    val queries = rdd.flatMap { grid =>
      var ret: List[PixelValue] = Nil
      for (line <- 0 until queryPts.value.length) {
        for (qpt <- 0 until queryPts.value(line).length) {
          if (grid.intersects(queryPts.value(line)(qpt)._1, queryPts.value(line)(qpt)._2, r.value)) {
            val num = grid.query_point_count(queryPts.value(line)(qpt)._1, queryPts.value(line)(qpt)._2, r.value)
            if (num != 0) ret ::= pixelConstructor(line, qpt, num)
          }
        }
      }
      ret

    }
    val collected = queries.collect()
    val ret = Array.fill(pts.length)(Array[Int]())
    for (i <- 0 until pts.length) ret(i) = Array.fill(pts(i).length)(0)
    collected.foreach { elem =>
      ret(elem.x)(elem.y) += elem.value
    }
    ret
  }

  def count: Long = rdd.count()

  def destroy(): Unit = {
    rdd.unpersist(blocking = true)
  }

  def printSuccess: Unit = {
    rdd.foreach(i => println("Finished Successfully"))
  }

}
