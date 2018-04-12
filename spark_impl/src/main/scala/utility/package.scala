

package object utility {
    type Index = Int
    
//    type IndexPair= (Index,Index)
    type DoublePair = (Double,Double)
    
    
    class IndexPair(val v:Int=0) extends AnyVal with Serializable {
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
    
    
    class PixelValue(val _hidden:Long=0L) extends AnyVal with Serializable {
      
      def x:Int = {
        (_hidden >> 48).toInt 
      }
      
      def y:Int = {
        (_hidden << 16 >> 48).toInt
      }
      
      def value:Int = {
        (_hidden << 48 >> 48).toInt
      }
      private def pos:Int = {
        (_hidden >> 32).toInt
      }
    }
    
    def pixelConstructor(x:Int=0,y:Int=0,value:Int=0):PixelValue = {
      val pos = (x << 16) + y
      new PixelValue((pos.toLong << 32) + value.toLong)
    }
}