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
import spatialrdd.partitioners.BalancedColumnPartitioner
import scala.collection.JavaConverters._

import java.util.ArrayList
import scala.util.Random
import java.io._
import spatialrdd.RDDGridProperty

object Main extends App {


  private var rddGrid: RDDGridProperty = _
  private var filename:String = "/tmp/lenssim_tmpfile"

  def helloWorld() = {
    println("Hello world!")
  }

  def TestSuite(ctx:JavaRDD[Int]) = {
    TestPixels(ctx)
  }

  def setFile(fname:String) = filename = fname

  def TestPixels(ctx:JavaRDD[Int]) = {
    println("Test Pixels")
    val sc = ctx.context
    val width = 10000
    val height = 10000
    val partitioner = new BalancedColumnPartitioner()
    val testPixels = sc.range(0,(width*height).toLong,1,256)
    val testPix2 = testPixels.map(i => new XYDoublePair(Random.nextDouble()*100,Random.nextDouble()*100))
    rddGrid = new RDDGrid(testPix2, partitioner)
    queryPoints(25.0,25.0,75.0,75.0,5,5,0.1,ctx,verbose = true)
  }

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
    ctx:JavaRDD[Int]): Unit = {
    val sc = ctx.context
    val stars = scala.io.Source.fromFile(starsfile).getLines().toArray.map{row => 
      val starInfoArr = row.split(",").map(_.toDouble)
      (starInfoArr(0),starInfoArr(1),starInfoArr(2))
    }
    
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
      width.toDouble,
      height.toDouble)
    val formattedPixels = pixels.mapPartitions(longIter => {
      longIter.map{long => 
        new XYIntPair(long.toInt % width,long.toInt/width)
      }
    },true)
    val mappedPixels = rayTracer(formattedPixels, sc.broadcast(parameters))//.cache()
    mappedPixels.collect()
    //Now need to construct the grid
    // val partitioner = new ColumnPartitioner()
    //val partitioner = new BalancedColumnPartitioner

    //rddGrid = new RDDGrid(mappedPixels, partitioner)
  }

  private def mkGrid(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int):Array[Array[(Double,Double)]] = {
    val ret = Array.fill(xDim)(Array.fill(yDim)((0.0,0.0)))
    val xStep = (x1 - x0)/(xDim.toDouble)
    val yStep = (y1 - y0)/(yDim.toDouble)
    val generator = (x:Double,y:Double) => (x0+xStep*x,y1-yStep*y)
    for (i <- 0 until xDim; j <- 0 until yDim) {
      ret(i)(j) = generator(i.toDouble,j.toDouble)
    }
    ret
  }
  private def makeGrid(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int) = {
    val ret = mkGrid(x0,y0,x1,y1,xDim,yDim)
    for (i <- ret) println(i.mkString(","))
  }

  private def mkGridWithIndex(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int) = {
    val ret = mkGrid(x0,y0,x1,y1,xDim,yDim)
    (for (i <- 0 until ret.length) yield {
      (for (j <- 0 until ret(0).length) yield new XYDoublePair(ret(i)(j)._1,ret(i)(j)._2)).toArray
    }).toArray
  }

  def queryPoints(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int,radius: Double,ctx:JavaRDD[Int],verbose:Boolean = false) = {
    println("Querying Points")
    val ptsFormatted = mkGridWithIndex(x0,y0,x1,y1,xDim,yDim)
    val sc = ctx.context
    println("Made coordinate plane. Now broadcasting to SpatialRDD")
    val retArr = rddGrid.queryPoints(ptsFormatted, radius, sc,verbose = verbose)
    println("Done Querying. Now onto formatting to return.")
    writeFile(retArr)
  }

  private def writeFile(data:Array[Array[Int]]):Unit = {
    val writer = new PrintWriter(new File(filename))
    val dString = data.map(_.mkString(",")).mkString(":")
    writer.write(dString)
    writer.close()
  }
}
