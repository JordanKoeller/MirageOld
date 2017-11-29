package lensing

import org.apache.spark.rdd.RDD
import org.apache.spark.broadcast.Broadcast

class RayParameters(val stars:Array[RayParameters.Star],
    val pointConstant:Double,
    val sisConstant:Double,
    val shearMag:Double,
    val shearAngle:Double,
    val dTheta:Double,
    val centerX:Double,
    val centerY:Double,
    val height:Double,
    val width:Double)

object RayParameters {
  case class Star(x:Double,y:Double,mass:Double)
  
  def apply(stars:RDD[(Double,Double,Double)],
            pointConstant:Double,
            sisConstant:Double,
            shearMag:Double,
            shearAngle:Double,
            dTheta:Double,
            centerX:Double,
            centerY:Double,
            height:Double,
            width:Double):RayParameters = {
    val starsFormatted = stars.collect().map(star => Star(star._1,star._2,star._3))
    new RayParameters(starsFormatted,
        pointConstant,
        sisConstant,
        shearMag,
        shearAngle,
        dTheta,
        centerX,
        centerY,
        height,
        width)
    
  }
}