

package object utility {
    type Index = Int
    
//    type IndexPair= (Index,Index)
    type DoublePair = (Double,Double)
    
    
    class IndexPair(val v:Int=0) extends AnyVal{
      def _2:Short = {
        ((v << 16) >> 16).toShort
      }
      
      
      
      def _1:Short ={
         (v >> 16).toShort 
      }
      
     override def toString():String = {
        "(" + this._1+","+this._2+")"
      }
    }
//    def mkPair(x:Index, y:Index):IndexPair = {
//    		new IndexPair((x.toInt << 16) + y.toInt)
//    }
    
    def mkPair(x:Int, y:Int):IndexPair = {
    		new IndexPair((x << 16) + y)
    }
}