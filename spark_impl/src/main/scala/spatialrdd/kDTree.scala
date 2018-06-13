//package spatialrdd


sealed class Node(val indI: Int,val indJ: Int,var split:Double,var upper:Node, var lower:Node) {
  def size: Int = indJ - indI
  
  override def toString() = "Node"
  
  def print = {
    println("Node with " + size + " elements from " + indI + " to " + indJ)
  }
  
  def search(x:Double,y:Double,r:Double,xSplit:Boolean):Int = {
    
    ???
  }
  
  def overlaps(x:Double,y:Double,r:Double,xSplit:Boolean):Boolean = {
    
    ???
  }
  
  def containedBy(x:Double,y:Double,r:Double,xSplit:Boolean):Boolean = {
    ???
  }
}




class kDTree(xx: IndexedSeq[Double], yy: IndexedSeq[Double], index: Array[Int], branchSize: Int) { // extends SpatialData {

  private val root = new Node(0, index.last, 0.0, null, null)
  
  private var numNodes = 0

  private var nodeDescs:Array[Double] = Array() //Array where groups of 4 are bottom left, top right of nodes
  def size: Int = {
    index.size
  }
  //  def query_point_count(x: Double, y: Double, r: Double): Int = {
  //    ???
  //  }
//    def query_points(pts: Iterator[((Int, Int), (Double, Double))], r: Double): Iterator[((Int, Int), Int)] = {
//      ???
//    }
  //  def intersects(x: Double, y: Double, r: Double): Boolean = {
  //    ???
  //  }
  
  def query_point_count(x:Double,y:Double,r:Double):Int = {
    
    ???
  }
  
  def recurs_search(nd:Node,x:Double,y:Double,r:Double,xSplit:Boolean):Int = {
    var counts = 0
    if (nd.containedBy(x,y,r,xSplit)) {
      counts += nd.size
    }
    else if (nd.lower == null && nd.upper == null) counts += nd.search(x, y, r, xSplit)
    else {
      // Needs to inform nodes if they are lesser or greater than splits
      if (nd.lower.overlaps(x, y, r,!xSplit)) counts += recurs_search(nd.lower,x,y,r,!xSplit)
      if (nd.upper.overlaps(x, y, r,!xSplit)) counts += recurs_search(nd.upper,x,y,r,!xSplit)
    }
    counts
    
    ???
  }
  
  
  
  def printt:Unit = print(root)
  
  def print(nd:Node):Unit = {
    nd.print
    if (nd.lower != null) {
      print(nd.lower)
    }
    if (nd.upper != null) {
      print(nd.upper)
    }
  }

  private def recur_nodes(nd: Node, ax: Char): Unit = {
    if (nd.size > branchSize) {
      numNodes += 2
      val k = (nd.indJ - nd.indI) / 2
      val n = nd.indJ - nd.indI
      if (ax == 'A') {
        selecti(k, n, xx, nd.indI)
        val split = xx(k + nd.indI)
        nd.split = split
        val n1 = new Node(nd.indI, k + nd.indI, 0.0, null, null)
        recur_nodes(n1, 'B')
        val n2 = new Node(k + nd.indI, nd.indJ, 0.0, null, null)
        recur_nodes(n2, 'B')
        nd.lower = n1
        nd.upper = n2
      } else {
        selecti(k, n, yy, nd.indI)
        val split = yy(k + nd.indI)
        nd.split = split
        val n1 = new Node(nd.indI, k + nd.indI, 0.0, null, null)
        recur_nodes(n1, 'A')
        val n2 = new Node(k + nd.indI, nd.indJ, 0.0, null, null)
        recur_nodes(n2, 'A')
        nd.lower = n1
        nd.upper = n2
      }
    }
  }

  def selecti(k: Int, n: Int, arr: IndexedSeq[Double], start: Int): Int = {
    var ir = n - 1
    var l = 0
    var i = 0
    var j = 0
    var ia = 0
    var a = 0.0
    while (true) {
      if (ir <= l + 1) {
        if (ir == l + 1 && arr(index(ir + start)) < arr(index(l + start))) swap(l + start, ir + start, index)
        return index(k + start)
      } else {
        val mid = (l + ir) >> 1
        swap(mid + start, l + 1 + start, index)
        if (arr(index(l + start)) > arr(index(ir + start))) swap(l + start, ir + start, index)
        if (arr(index(l + 1 + start)) > arr(index(ir + start))) swap(l + 1 + start, ir + start, index)
        if (arr(index(l + start)) > arr(index(l + 1 + start))) swap(l + start, l + 1 + start, index)
        i = l + 1
        j = ir
        ia = index(l + 1 + start)
        a = arr(ia)
        var flag = true
        while (flag) {
          do { i += 1 } while (arr(index(i + start)) < a)
          do { j -= 1 } while (arr(index(j + start)) > a)
          if (j < i) flag = false
          else swap(i + start, j + start, index)
        }
        index(l + 1 + start) = index(j + start)
        index(j + start) = ia
        if (j >= k) ir = j - 1
        if (j <= k) l = i
      }
    }
    println("Broke selecti")
    -1
  }
  private def swap[T](a: Int, b: Int, array: Array[T]) {
    val tmp = array(a)
    array(a) = array(b)
    array(b) = tmp
  }
  
  private def set_boxes():Unit = {
    
  }
  
  
  recur_nodes(root, 'A')
  set_boxes()
  println("Done recursing")
}

object kDTree {

  def apply(values: IndexedSeq[(Double, Double)], binSize: Int = 16): kDTree = {
    val xcoords = values.map(_._1)
    val ycoords = values.map(_._2)
    val indices = Array.range(0, xcoords.length)
    new kDTree(xcoords, ycoords, indices, binSize)
  }

}