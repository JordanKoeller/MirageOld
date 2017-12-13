package spatialrdd

import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import org.apache.spark.Partitioner
import spatialrdd.partitioners.SpatialPartitioning

import org.apache.spark.storage.StorageLevel

class PaddedRDDGrid(data: RDD[XYDoublePair], partitioner: SpatialPartitioning) extends RDDGridProperty {

	data.persist(StorageLevel.MEMORY_AND_DISK)


  sealed class StraightPartition() extends Partitioner {
  	def getPartition(key:Any):Int = {
  		key match {
  			case elem:Int => elem
  		}
  	}

  	def numPartitions:Int = 256
  }


  def queryPoints(pts: Array[Array[XYDoublePair]], radius: Double, sc: SparkContext,verbose:Boolean = false): Array[Array[Int]] = {
    val rddProfiled = partitioner.profileData(data)
    val rddWithDuplicates = data.flatMap{elem =>
    	val partitions = partitioner.getPartitions(elem, radius)
    	partitions.toArray.map(_ -> elem)
    }
    val realPartitioner = new StraightPartition()
    val partitionedRDD = rddWithDuplicates.partitionBy(realPartitioner)
    val grids = partitionedRDD.glom().mapPartitions(arrr => arrr.map(arr => VectorGrid(arr.map(i => (i._2.x,i._2.y))))).persist(StorageLevel.MEMORY_AND_DISK)
    val groupings = Array.fill(partitioner.numPartitions)(collection.mutable.ListBuffer[(XYIntPair, XYDoublePair)]())

    for (i <- 0 until pts.size; j <- 0 until pts(0).size) {
    	val partition = partitioner.getPartition(pts(i)(j))
    	groupings(partition) += new XYIntPair(i,j) -> pts(i)(j)
    }

    val broadcastedGroups = sc.broadcast(groupings)
    val ret = Array.fill(pts.size, pts(0).size)(0)
    var counter2 = 0
    println("Now querying the grids")
    val countRDD = grids.mapPartitionsWithIndex((ind, gridInIterator) => {
      val grid = gridInIterator.next()
      broadcastedGroups.value(ind).map{ elem =>
        elem._1 -> grid.query_point_count(elem._2.x, elem._2.y, radius)
      }.iterator
    }, true)
    countRDD.collect().foreach { elem => ret(elem._1.x)(elem._1.y) += elem._2 }
    println("DONE")
    ret
  }

  def count:Long = data.count()

}
