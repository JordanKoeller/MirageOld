package lensing

import spatialrdd.XYDoublePair
import spatialrdd.XYIntPair
import org.apache.spark.rdd.RDD
import org.apache.spark.broadcast.Broadcast

class RayTracer() {
  
  def apply(pixels:RDD[XYIntPair],p:Broadcast[RayParameters]):RDD[XYDoublePair] = {
    val pi2 = math.Pi/2.0
    val ret = pixels.mapPartitions(pixelIter => {
      pixelIter.map{pixel => 
        var retX = 0.0
        var retY = 0.0
        val incidentAngleX = (pixel.x - p.value.width)*p.value.dTheta
        val incidentAngleY = (p.value.height - pixel.y)*p.value.dTheta
      
      // Point sources
      for (star <- p.value.stars) {
        val deltaRX = incidentAngleX - star.x
        val deltaRY = incidentAngleY - star.y
        val r = deltaRX*deltaRX+deltaRY*deltaRY
        if (r != 0.0) {
          retX += deltaRX*star.mass*p.value.pointConstant/r
          retY += deltaRY*star.mass*p.value.pointConstant/r
        }
      }
      
      //SIS constant
        val deltaRX = incidentAngleX - p.value.centerX
        val deltaRY = incidentAngleY - p.value.centerY
        val r = math.sqrt(deltaRX*deltaRX+deltaRY*deltaRY)
        if (r != 0.0) {
          retX += deltaRX*p.value.sisConstant/r
          retY += deltaRY*p.value.sisConstant/r
        }
      
      //Shear
        val phi = 2*(pi2 - p.value.shearAngle)-math.atan2(deltaRY,deltaRX)
        retX += p.value.shearMag*r*math.cos(phi)
        retY += p.value.shearMag*r*math.sin(phi)
        new XYDoublePair(deltaRX-retX,deltaRY-retY)
      }
    },true)
    println("Done")
    ret
  }
}
