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
    println(rddGrid.count)
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
    val parameters = RayParameters(stars,
      pointConstant,
      sisConstant,
      shearMag,
      shearAngle,
      dTheta,
      centerX,
      centerY,
      width.toDouble/2,
      height.toDouble/2)
    val formattedPixels = pixels.mapPartitions(longIter => {
      longIter.map{long => 
        new XYIntPair(long.toInt % width,long.toInt/width)
      }
    },true)
    val mappedPixels = rayTracer(formattedPixels, sc.broadcast(parameters)).cache()
    //Now need to construct the grid
    val partitioner = new ColumnPartitioner()
    rddGrid = new RDDGrid(mappedPixels, partitioner)
    mappedPixels.unpersist()
  }

  def mkGrid(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int):Array[Array[(Double,Double)]] = {
    val ret = Array.fill(xDim)(Array.fill(yDim)((0.0,0.0)))
    val xStep = (x1 - x0)/(xDim.toDouble)
    val yStep = (y1 - y0)/(yDim.toDouble)
    val generator = (x:Double,y:Double) => (x0+xStep*x,y1-yStep*y)
    for (i <- 0 until xDim; j <- 0 until yDim) {
      ret(i)(j) = generator(i.toDouble,j.toDouble)
    }
    ret
  }
  def makeGrid(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int) = {
    val ret = mkGrid(x0,y0,x1,y1,xDim,yDim)
    for (i <- ret) println(i.mkString(","))
  }

  def mkGridWithIndex(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int) = {
    val ret = mkGrid(x0,y0,x1,y1,xDim,yDim)
    (for (i <- 0 until ret.length) yield {
      (for (j <- 0 until ret(0).length) yield new XYDoublePair(ret(i)(j)._1,ret(i)(j)._2)).toArray
    }).toArray
  }

  def queryPoints(x0:Double,y0:Double,x1:Double,y1:Double,xDim:Int,yDim:Int,radius: Double,ctx:JavaRDD[Int]):ArrayList[ArrayList[Double]] = {
    println("Querying Points")
    val ptsFormatted = mkGridWithIndex(x0,y0,x1,y1,xDim,yDim)
    val sc = ctx.context
    println("Made coordinate plane. Now broadcasting to SpatialRDD")
    val retArr = rddGrid.queryPoints(ptsFormatted, radius, sc)
    println("Done Querying. Now onto formatting to return.")
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
    println("Done formatting")
    ret
  }
}
