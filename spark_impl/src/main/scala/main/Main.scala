package main

import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import org.apache.spark.api.java.JavaRDD

import lensing.RayParameters
import lensing.RayTracer
import spatialrdd.MinMax2D
import spatialrdd.RDDGrid
import spatialrdd.XYDoublePair
import spatialrdd.XYIntPair
import spatialrdd.partitioners.ColumnPartitioner
import scala.collection.JavaConverters._


import java.util.ArrayList

object Main extends App {


  private var rddGrid: RDDGrid = _

  def helloWorld() = {
    println("Hello world!")
  }

  def createRDDGrid(
    starsArr: ArrayList[ArrayList[Double]],
    pointConstant: Double,
    sisConstant: Double,
    shearMag: Double,
    shearAngle: Double,
    dTheta: Double,
    centerX: Double,
    centerY: Double,
    width: Int,
    height: Int,
    ctx:JavaRDD[Int]): Unit = {
    val sc = ctx.context
    val starsS = collection.mutable.Buffer[(Double,Double,Double)]()
    if (starsArr.size() > 0) {
	println(starsArr.get(0).get(0).getClass())
      for (i <- 0 until starsArr.size()) {
        val star = starsArr.get(i)
        val starT = (star.get(0),star.get(1),star.get(2))
        starsS += starT
      }
    }
   val stars = starsS//.toArray
    
    //Construction of RDD, mapping of RDD to ray-traced source plane locations
    val rayTracer = new RayTracer()
    val pixels = sc.range(0, (width * height).toLong, 1)
    println("Initialized pixels variable with size "+pixels.count())
    val parameters = RayParameters(stars,
      pointConstant,
      sisConstant,
      shearMag,
      shearAngle,
      dTheta,
      centerX,
      centerY,
      width.toDouble,
      height.toDouble)
    val formattedPixels = pixels.mapPartitions(longIter => {
      longIter.map{long => 
        new XYIntPair(long.toInt / width, long.toInt % width)
      }
    },true)
    val mappedPixels = rayTracer(formattedPixels, sc.broadcast(parameters)).cache()
    //Now need to construct the grid
    val partitioner = new ColumnPartitioner()
    rddGrid = new RDDGrid(mappedPixels, partitioner)
    mappedPixels.unpersist()
    println("called new RDDGrid")
  }

  def queryPoints(pts: ArrayList[ArrayList[Double]], radius: Double,ctx:JavaRDD[Int]):ArrayList[ArrayList[Double]] = {
    val ptsFormatted = pts.iterator().asScala.toArray.map(lst => ((lst.get(0).toInt,lst.get(1).toInt),(lst.get(2).toDouble,lst.get(3).toDouble)))
    val sc = ctx.context
    val minMax = ptsFormatted.aggregate(MinMax2D())((lastExtremes, elem) => {
      val x = elem._1._2
      val y = elem._1._2
      if (x > lastExtremes.xMax) lastExtremes.xMax = x
      if (y > lastExtremes.yMax) lastExtremes.yMax = y
      if (x < lastExtremes.xMin) lastExtremes.xMin = x
      if (y < lastExtremes.yMin) lastExtremes.yMin = y
      lastExtremes
    }, (mm1, mm2) => {
      val ret = MinMax2D()
      if (mm1.xMin < mm2.xMin) ret.xMin = mm1.xMin else ret.xMin = mm2.xMin
      if (mm1.xMax > mm2.xMax) ret.xMax = mm1.xMax else ret.xMax = mm2.xMax
      if (mm1.yMin < mm2.yMin) ret.yMin = mm1.yMin else ret.yMin = mm2.yMin
      if (mm1.yMax > mm2.yMax) ret.yMax = mm1.yMax else ret.yMax = mm2.yMax
      ret
    })

    val argArr = Array.fill((minMax.xMax - minMax.xMin).toInt, (minMax.yMax - minMax.yMin).toInt)(new XYDoublePair(0, 0))
    ptsFormatted.map { i =>
      argArr(i._1._1)(i._1._2) = new XYDoublePair(i._2._1, i._2._1)
    }
    val retArr = rddGrid.queryPoints(argArr, radius, sc)
    val retSeq = for (i <- 0 until retArr.size;j <- 0 until retArr(0).size) yield {
      new XYIntPair(i,j) -> retArr(i)(j)
    }
    val retArr2 = retSeq.map{e =>
      val arr = new ArrayList[Double]()
      arr.add(e._1.x.toDouble)
      arr.add(e._1.y.toDouble)
      arr.add(e._2)
      arr
    }
    val ret = new java.util.ArrayList[ArrayList[Double]]()
    for (elem <- retArr2) ret.add(elem)
    ret
  }
}
