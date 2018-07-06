import numpy
import numpy as np
from pyspark.rdd import RDD

class NumericRDD(object):
    '''
RDD subtype, for use with only Numeric types. 
Internally, this RDD gloms all its data, and stores
the glommed data as Numpy arrays. From there,
any mathematical operations on the NumericRDD
calls numeric functions on the numpy arrays inside.
    '''

    def __init__(self, rdd=None,needsFormatting=True,*args,**kwargs):
        if rdd:
            self.constructFrom(rdd,needsFormatting)

    def constructFrom(self,rdd,needsFormatting=True):
        if needsFormatting:
            assert isinstance(rdd,RDD), "rdd must be a RDD of numeric type"
    #        assert isinstance(e1,np.ndarray) or isinstance(e1,int) or isinstance(e1,float) or isinstance(e1,complex), "rdd must be a RDD of numeric type"
            self._rdd = rdd.glom().map(np.array)
        else:
            self._rdd = rdd

    def map(self,fn):
        return self._rdd.map(fn)

    def collect(self):
        #expand back to a list, then collect
        return np.array(self._rdd.collect()).flatten()

    @property
    def rdd(self):
        return self._rdd

    def __add__(self,other):
        return NumericRDD(self.map(lambda x:other + x),needsFormatting=False)

    def __sub__(self,other):
        return NumericRDD(self.map(lambda x:x - other),needsFormatting=False)

    def __mul__(self,other):
        return NumericRDD(self.map(lambda x:x * other),needsFormatting=False)

    def __truediv__(self,other):
        return NumericRDD(self.map(lambda x:x/other),needsFormatting=False)

    def __floordiv__(self,other):
        return NumericRDD(self.map(lambda x:x // other),needsFormatting=False)

    def __mod__(self,other):
        return NumericRDD(self.map(lambda x:x % other),needsFormatting=False)

    def __pow__(self,other):
        return NumericRDD(self.map(lambda x:x ** other),needsFormatting=False)

    def __mul__(self,other):
        return NumericRDD(self.map(lambda x:x * other),needsFormatting=False)

    def __radd__(self,other):
        return NumericRDD(self.map(lambda x:other + x),needsFormatting=False)

    def __rsub__(self,other):
        return NumericRDD(self.map(lambda x:x - other),needsFormatting=False)

    def __rmul__(self,other):
        return NumericRDD(self.map(lambda x:x * other),needsFormatting=False)

    def __rtruediv__(self,other):
        return NumericRDD(self.map(lambda x:x/other),needsFormatting=False)

    def __rfloordiv__(self,other):
        return NumericRDD(self.map(lambda x:x // other),needsFormatting=False)

    def __rmod__(self,other):
        return NumericRDD(self.map(lambda x:x % other),needsFormatting=False)

    def __rpow__(self,other):
        return NumericRDD(self.map(lambda x:x ** other),needsFormatting=False)

    def __neg__(self):
        return NumericRDD(self.map(lambda x: -x),needsFormatting=False)

    def __iadd__(self,other):
        self._rdd = self.map(lambda x:other + x)
        return self

    def __isub__(self,other):
        self._rdd = self.map(lambda x:x - other)
        return self        
    def __imul__(self,other):
        self._rdd = self.map(lambda x:x * other)
        return self
    def __itruediv__(self,other):
        self._rdd = self.map(lambda x:x/other)
        return self
    def __ifloordiv__(self,other):
        self._rdd = self.map(lambda x:x // other)
        return self
    def __imod__(self,other):
        self._rdd = self.map(lambda x:x % other)
        return self
    def __ipow__(self,other):
        self._rdd = self.map(lambda x:x ** other)
        return self
    def __neg__(self):
        self._rdd = self.map(lambda x: -x)
        return self