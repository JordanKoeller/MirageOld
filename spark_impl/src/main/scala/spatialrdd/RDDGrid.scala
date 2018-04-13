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
    val ret = glommed.map(arr => MemGrid(arr)).persist(StorageLevel.MEMORY_ONLY)
    ret
  }

  def query_2(gen: GridGenerator, radius: Double, sc: SparkContext, verbose: Boolean = false): Array[Array[Int]] = {
    println("Broadcasting generator")
    val bgen = sc.broadcast(gen)
    val r = sc.broadcast(radius)
    val queries = rdd.flatMap { grid =>
      gen.flatMap { qPt =>
        if (grid.intersects(qPt.x, qPt.y, r.value)) {
          val num = grid.query_point_count(qPt.x, qPt.y, r.value)
          if (num != 0) pixelConstructor(qPt.px, qPt.py, num) :: Nil else Nil
        } else List[PixelValue]()
      }
    }

    val collected = queries.collect()
    val ret = Array.fill(gen.xDim, gen.yDim)(0)
    collected.foreach { elem =>
      ret(elem.x)(elem.y) += elem.value
    }
    ret
  }

  def count: Long = rdd.count()

}
