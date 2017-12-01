package lensing

import org.apache.spark.rdd.RDD
import org.apache.spark.broadcast.Broadcast

class RayParameters(val stars:Seq[RayParameters.Star],
    val pointConstant:Double,
    val sisConstant:Double,
    val shearMag:Double,
    val shearAngle:Double,
    val dTheta:Double,
    val centerX:Double,
    val centerY:Double,
    val height:Double,
    val width:Double) extends Serializable

object RayParameters {
  case class Star(x:Double,y:Double,mass:Double)
  
  def apply(stars:Seq[(Double,Double,Double)],
            pointConstant:Double,
            sisConstant:Double,
            shearMag:Double,
            shearAngle:Double,
            dTheta:Double,
            centerX:Double,
            centerY:Double,
            height:Double,
            width:Double):RayParameters = {
    val starsFormatted = stars.map(star => Star(star._1,star._2,star._3))
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
