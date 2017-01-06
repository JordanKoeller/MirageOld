package utility

import collection.mutable

class SpatialTree[Value](xmin: Double, xmax: Double, ymin: Double, ymax: Double) {
//  println("Dims")
//  println(xmin + " " + xmax + " " + ymin + " " + ymax )
  private val MaxObjs = 5
  private var sz: Int = 0
  var cntr = 0

  sealed case class Datum(x: Double, y: Double, datum: Value)

  sealed class Node(cx: Double, cy: Double, sx: Double, sy: Double,
      val objects: mutable.Buffer[Datum], var children: Array[Node]) {
    def whichChild(obj: Datum): Int = {
      (if (obj.x > cx) 1 else 0) + (if (obj.y > cy) 2 else 0)
    }
    def makeChildren() {
      children = Array(
        new Node(cx - sx / 4, cy - sy / 4, sx / 2, sy / 2, mutable.Buffer(), null),
        new Node(cx + sx / 4, cy - sy / 4, sx / 2, sy / 2, mutable.Buffer(), null),
        new Node(cx - sx / 4, cy + sy / 4, sx / 2, sy / 2, mutable.Buffer(), null),
        new Node(cx + sx / 4, cy + sy / 4, sx / 2, sy / 2, mutable.Buffer(), null))
    }
    def overlap(obj: OrderedPair, radius: Double): Boolean = {
      obj.x - radius < cx + sx / 2 && obj.x + radius > cx - sx / 2 &&
        obj.y - radius < cy + sy / 2 && obj.y + radius > cy - sy / 2
    }
  }

  private val root = new Node((xmax + xmin) / 2, (ymax + ymin) / 2, xmax - xmin, ymax - ymin,
    mutable.Buffer[Datum](), null)

  def add(datum: Value, position: OrderedPair) {
   // println("trying")
    if (!(position.x > xmin && position.x < xmax && position.y > ymin && position.y < ymax)) {
     // println("Out of Bounds Exception")
      return
    }
   // println("Adding")
    addRecur(Datum(position.x, position.y, datum), root)
    sz += 1
  //  println(sz)
  }

  private def addRecur(obj: Datum, n: Node) {
    //  println(cntr)
   // Thread.sleep(1000)
    if (n.children == null) {
      if (n.objects.length < MaxObjs) {
      //  println("Case 1")

        n.objects += obj
        //       println("Added Child")
      } else {
      //  println("Case 2")
        n.makeChildren()
        for (o <- n.objects) {
          addRecur(o, n.children(n.whichChild(o)))
        }
        n.objects.clear
        addRecur(obj, n.children(n.whichChild(obj)))
      }
    } else {
     // println("Case 3")
      addRecur(obj, n.children(n.whichChild(obj)))
    }
  }
  def searchNeighbors(obj: OrderedPair, radius: Double): mutable.Buffer[Value] = {
    val ret = mutable.Buffer[Value]()
    searchRecur(obj, radius, root, ret)
    ret
  }

  private def searchRecur(obj: OrderedPair, radius: Double, n: Node, ret: mutable.Buffer[Value]) {
    //  println("Searching")
    if (n.children == null) {
      //    println("Adding to buffer")
      ret ++= (n.objects.filter(o => distance(OrderedPair(o.x, o.y), obj) < radius)).map(i => i.datum)
    } else {
      for (child <- n.children; if (child.overlap(obj, radius)))
        searchRecur(obj, radius, child, ret)
    }
  }

  def size(): Int = { sz }

  def clear(): Unit = {
    root.objects.clear()
    root.children = null
    sz = 0
  }

  private def distance(a: OrderedPair, b: OrderedPair): Double = {
    val dx = a.x - b.x
    val dy = a.y - b.y
    math.sqrt(dx * dx + dy * dy)
  }
}