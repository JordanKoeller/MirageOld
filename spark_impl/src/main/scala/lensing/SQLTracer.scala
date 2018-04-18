package lensing

import org.apache.spark.sql.Dataset
import org.apache.spark.broadcast.Broadcast
import org.apache.spark.sql.Row
import org.apache.spark.sql.functions._

class SQLTracer extends Serializable {
  def apply(data: Dataset[Long], p: Broadcast[RayParameters]) = {
    val spark = data.sparkSession
    import spark.implicits._
    val df = data.toDF("value")
    val pairs = data.select('value % p.value.width as "x", 'value / p.value.width as "y")
    var angles = pairs.select(
      ('x - p.value.width / 2.0) * p.value.dTheta as "angleX",
      (-'y + p.value.height / 2.0) * p.value.dTheta as "angleY",
      'x * 0.0 as "retX", 'y * 0.0 as "retY")
    for (star <- p.value.stars) {
      val deltas = angles.select(
        'angleX, 'angleY, 'angleX - star.x as "dx", 'angleY - star.y as "dy", 'retX, 'retY)
      val withR = deltas.select('angleX, 'angleY, 'dx, 'dy, 'dx * 'dx + 'dy * 'dy as "r", 'retX, 'retY)
      angles = withR.select('angleX,
        'angleY,
        'retX + 'dx * star.mass * p.value.pointConstant / 'r as "retX",
        'retY + 'dy * star.mass * p.value.pointConstant / 'r as "retY")
    }

    //Calculating SIS constant now
    val siscomponents = angles.select(
      'angleX,
      'angleY,
      'angleX - p.value.centerX as "dx",
      'angleY - p.value.centerY as "dy",
      'retX,
      'retY)
    val withSisR = siscomponents.select(
      'angleX,
      'angleY,
      'retX,
      'retY,
      sqrt('dx * 'dx + 'dy * 'dy) as "r",
      'dx,
      'dy)

    val withSis = withSisR.select(
      'angleX,
      'angleY,
      'retX + 'dx * p.value.sisConstant / 'r as "retX",
      'retY + 'dy * p.value.sisConstant / 'r as "retY",
      'r,
      'dx,
      'dy)

    //Now need to get shear factored int

    val phi = withSis.select(
      'angleX,
      'angleY,
      'retX,
      'retY,
      'r,
      'dx,
      'dy,
      -atan2('dy, 'dx) + 2.0 * (math.Pi / 2.0 - p.value.shearAngle) as "phi")
    phi.select(
      'dx - ('retX + 'r * cos('phi) * p.value.shearMag) as "_1",
      'dy - ('retY + 'r * sin('phi) * p.value.shearMag) as "_2")

    //    angles.select('angleX as "_1", 'angleY as "_2")
  }
}