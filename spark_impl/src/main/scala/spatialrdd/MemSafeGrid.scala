// package spatialrdd
// import scala.collection.mutable
// import scala.util.Random 

// class MemGrid(data: IndexedSeq[(Double,Double)], bucketFactor: Int = 1) extends Serializable {
//   private val _hashX = equalHashing(data, (l: (Double,Double)) => l._1, math.sqrt(data.size).toInt * bucketFactor)
//   private val _hashY = equalHashing(data, (l: (Double,Double)) => l._2, math.sqrt(data.size).toInt * bucketFactor)
//   private val _buckets = _initBuckets()
//   def _initBuckets():Array[Array[mutable.ListBuffer[Int]]] = {
//     val numBucs = math.sqrt(data.size).toInt * bucketFactor
//     Array.fill(numBucs)(Array.fill(numBucs)(mutable.ListBuffer[Int]()))
//   }


//   for (i <- 0 until data.size) _insert_pt(i)

//   private def _hashFunction(xx: Double, yy: Double): XYIntPair = {
//     val x = _hashX(xx)
//     val y = _hashY(yy)
//     new XYIntPair(x, y)
//   }

//   private def _fetch_bucket(i:Int,j:Int):Int = {
//     try {
//       _buckets(i)(j).size
//     }
//     catch {
//       case e:ArrayIndexOutOfBoundsException => 0
//     }
//   }

//   private def _query_bucket(i:Int,j:Int,x:Double,y:Double,r2:Double, intArr:Array[Int], doubleArr:Array[Double]) = {
//     try {
//       if (_buckets(i)(j).size > 0) {
//         for (k <- _buckets(i)(j)) {
//           doubleArr(0) = data(k)._1
//           doubleArr(1) = data(k)._2
//           doubleArr(2) = doubleArr(0) - x
//           doubleArr(3) = doubleArr(1) - y
//           if (r2 >= doubleArr(2)*doubleArr(2) +doubleArr(3)*doubleArr(3)) intArr(5) += 1
//         }
//       }
//     }
//     catch {
//       case e:ArrayIndexOutOfBoundsException => Unit
//     }
//   }


//   private def _insert_pt(index: Int): Unit = {
//     val coords = _hashFunction(data(index)._1, data(index)._2)
//     _buckets(coords.x)(coords.y) += index
//   }

//   def size = data.size

//   def query_point_count(x: Double, y: Double, r: Double,rr:Double,intArr:Array[Int],doubleArr:Array[Double]): Int = {
//     //Fill in doubleArr Fields:
//     /*LEGEND
//     0 -> centerX
//     1 -> centerY
//     2 -> intRX
//     3 -> intRY
//     4 -> index Hypotenuse
//     5 -> counter


//     */
//     intArr(0) = _hashY(x)
//     intArr(1) = _hashY(y)
//     intArr(2) = intArr(0) - _hashX(x - r)
//     intArr(3) = intArr(1) - _hashX(y - r)
//     intArr(4) = intArr(2)*intArr(2)+intArr(3)*intArr(3)
//     intArr(5) = 0

//     for (i <- 1 until intArr(2)) {
//       intArr(5) += _fetch_bucket(intArr(0)+i,intArr(1))
//       intArr(5) += _fetch_bucket(intArr(0)-i,intArr(1))
//     }
//     for (i <- 1 until intArr(3)) {
//       intArr(5) += _fetch_bucket(intArr(0),intArr(1)+i)
//       intArr(5) += _fetch_bucket(intArr(0),intArr(1)-i)
//     }
//     _query_bucket(intArr(0),intArr(1),x,y,rr,intArr,doubleArr)
//     for (i <- 1 to intArr(2)) {
//       intArr(1) = (math.sqrt(intArr(4)-i*i)+1).toInt
//       for (j <- 1 to intArr(3)) {
//         if (i < intArr(2) && j < intArr(3)) {
//           intArr(5) += _fetch_bucket(intArr(0)+i,intArr(1)+j)
//           intArr(5) += _fetch_bucket(intArr(0)+i,intArr(1)-j)
//           intArr(5) += _fetch_bucket(intArr(0)-i,intArr(1)-j)
//           intArr(5) += _fetch_bucket(intArr(0)-i,intArr(1)+j)
//         }
//         else {
//           _query_bucket(intArr(0)+i,intArr(1),x,y,rr,intArr,doubleArr)
//           _query_bucket(intArr(0)+i,intArr(1),x,y,rr,intArr,doubleArr)
//           _query_bucket(intArr(0)-i,intArr(1),x,y,rr,intArr,doubleArr)
//           _query_bucket(intArr(0)-i,intArr(1),x,y,rr,intArr,doubleArr)
//         }
//       }
//     }
//     intArr(5)
//   }

//   def query_points(pts: Iterator[XYDoublePair], r: Double): Iterator[Int] = {
//     val doubleArr = Array.fill(6)(0.0)
//     val intArr = Array.fill(3)(0)
//     pts.map(pt => query_point_count(pt.x, pt.y, r, r*r, intArr,doubleArr))
//   }
// }

// object MemGrid {

//   val bucketFactor = 7

//   def apply(data: IndexedSeq[(Double, Double)]): MemGrid = {
//     val ret = new MemGrid(data, bucketFactor)
//     ret
//   }



//   def TestGrid() = {
//     val arr = Array.fill(500000)((Random.nextDouble()*100.0,Random.nextDouble()*100.0))
//     val grid = MemGrid(arr)
//     // (for (i <- 25 until 75; j <- 25 until 75) yield grid.query_point_count(i.toDouble,j.toDouble,5.0)).take(20) foreach println
//   }
// }
