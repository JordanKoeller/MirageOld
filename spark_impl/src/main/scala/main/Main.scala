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

object Main {

  val sc = SparkContext.getOrCreate()

  private var rddGrid: RDDGrid = _

  def createRDDGrid(
    stars: JavaRDD[(Double, Double, Double)],
    pointConstant: Double,
    sisConstant: Double,
    shearMag: Double,
    shearAngle: Double,
    dTheta: Double,
    centerX: Double,
    centerY: Double,
    width: Double,
    height: Double): Unit = {

    //Construction of RDD, mapping of RDD to ray-traced source plane locations
    val rayTracer = new RayTracer()
    val pixels = sc.range(0, (width * height).toLong, 1)
    val parameters = RayParameters(stars,
      pointConstant,
      sisConstant,
      shearMag,
      shearAngle,
      dTheta,
      centerX,
      centerY,
      width,
      height)
    val formattedPixels = pixels.map { long =>
      new XYIntPair(long.toInt / width.toInt, long.toInt % width.toInt)
    }
    val mappedPixels = rayTracer(formattedPixels, sc.broadcast(parameters))

    //Now need to construct the grid
    val partitioner = new ColumnPartitioner()
    rddGrid = new RDDGrid(mappedPixels, partitioner)
  }

  def queryPoints(pts: JavaRDD[((Int, Int), (Double, Double))], radius: Double):JavaRDD[(Int,Int,Double)] = {
    val ptsFormatted = pts.rdd.collect()
    val minMax = ptsFormatted.aggregate(MinMax2D())((lastExtremes, elem) => {
      val x = elem._1._1
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
    sc.parallelize(retSeq, 1).map(e => (e._1.x,e._1.y,e._2))
  }
}
