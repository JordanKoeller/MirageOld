package main

import java.io._

import org.apache.spark.api.java.JavaRDD
import org.apache.spark.sql.SparkSession

import lensing.RayParameters
import lensing.RayTracer
import spatialrdd.GridGenerator
import spatialrdd.RDDGrid
import spatialrdd.RDDGridProperty
//import spatialrdd.XYIntPair
import spatialrdd.partitioners.BalancedColumnPartitioner
import lensing.DataFrameRayTracer

import org.apache.spark.sql.functions._
import org.apache.spark.sql.Dataset
import org.apache.spark.sql.types.StructType
import org.apache.spark.sql.types.StructField
import org.apache.spark.sql.types.LongType
import org.apache.spark.sql.Row
import org.apache.spark.sql._

object Main extends App {

  private var rddGrid: RDDGridProperty = null
  private var filename: String = "/tmp/lenssim_tmpfile"


  def setFile(fname: String) = filename = fname

  def createRDDGrid(
    starsfile: String,
    pointConstant: Double,
    sisConstant: Double,
    shearMag: Double,
    shearAngle: Double,
    dTheta: Double,
    centerX: Double,
    centerY: Double,
    width: Int,
    height: Int,
    ctx: JavaRDD[Int]): Unit = {
    if (rddGrid != null) rddGrid.destroy()
    val sc = ctx.context
    val stars = scala.io.Source.fromFile(starsfile).getLines().toArray.map { row =>
      val starInfoArr = row.split(",").map(_.toDouble)
      (starInfoArr(0), starInfoArr(1), starInfoArr(2))
    }
    //Construction of RDD, mapping of RDD to ray-traced source plane locations
    val rayTracer = new RayTracer()
    val pixels = sc.range(0, (width * height).toLong, 1,1)
    val parameters = RayParameters(
      stars,
      pointConstant,
      sisConstant,
      shearMag,
      shearAngle,
      dTheta,
      centerX,
      centerY,
      width.toDouble,
      height.toDouble)

    val broadParams = sc.broadcast(parameters)
    val mappedPixels = rayTracer(pixels, broadParams)
    //Now need to construct the grid
    // val partitioner = new ColumnPartitioner()
    val partitioner = new BalancedColumnPartitioner

    rddGrid = new RDDGrid(mappedPixels, partitioner)
    broadParams.unpersist()
  }

  def queryPoints(x0: Double, y0: Double, x1: Double, y1: Double, xDim: Int, yDim: Int, radius: Double, ctx: JavaRDD[Int], verbose: Boolean = false) = {
    val sc = ctx.context
    val generator = new GridGenerator(x0, y0, x1, y1, xDim, yDim)
    val retArr = rddGrid.queryPointsFromGen(generator, radius, sc, verbose = verbose)
    rddGrid.printSuccess
    writeFile(retArr)
  }
  
  def sampleLightCurves(filename:String,radius:Double,ctx:JavaRDD[Int]) {
    val sc = ctx.context
    val lightCurves = scala.io.Source.fromFile(filename).getLines().toArray.map{row =>
      val queryLine = row.split(",").map{elem =>
        val pair = elem.split(":").map(_.toDouble)
        (pair.head,pair.last)
      }
      queryLine
    }
    val retArr = rddGrid.queryPoints(lightCurves,radius,sc,false)
    writeFile(retArr)
    
  }

  private def writeFile(data: Array[Array[Int]]): Unit = {
    val writer = new PrintWriter(new File(filename))
    val dString = data.map(_.mkString(",")).mkString(":")
    writer.write(dString)
    writer.close()
  }
}
