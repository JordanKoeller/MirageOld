from abc import ABC, abstractmethod, abstractproperty
import numpy as np
class Partitioner(ABC):
    '''
    Abstract class for partitioning spatial data across multiple machines.
    Used in conjunction with the Spark Engine for efficient queries of spatial data.

    Subclasses must impliment the following functions:
    - :func:`paritioner(self,data_element)`
    - :func:`fit_for_data(self,rdd)`

    And the following attributes:
    - :func:`num_partitions`

    Note: Must pass in a spark context upon initialization
    '''

    def __init__(self):
        pass

    def partition(self,rdd):
        rdd = rdd.cache()
        self.read_rdd(rdd)
        flattened = rdd.flatMap(lambda x:x)
        kv = flattened.keyBy(lambda x:x[0])
        ret =  kv.partitionBy(self.num_partitions,self.hash_function)
        return ret.values().glom().map(lambda x:np.array(x))

    @abstractmethod
    def read_rdd(self,rdd):
        pass

    @abstractmethod
    def hash_function(self,pixel):
        pass

    @abstractproperty
    def num_partitions(self):
        pass

