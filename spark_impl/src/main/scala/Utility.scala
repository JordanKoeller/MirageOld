

object Utility {

	def ints2Long(x:Int, y:Int):Long = {
		(x.toLong << 32) | (y & 0xffffffffL)		
	}

	def long2Ints(l:Long):(Int,Int) = {
		((l >> 32).toInt, l.toInt)
	}

}