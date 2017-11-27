from . import Partitioner

class ColumnPartitioner(Partitioner):
    '''
    Simple partitioning scheme that divides the dataset into columns.

    Calling :func:`fit_for_data` determines the maximum and minimum x values and sets up a hash function to hash x-values of data points into a specific column. All columns are equivalently sized.
    '''

    def __init__(self):
        Partitioner.__init__(self)

    def read_rdd(self,rdd,num_partitions = None):
        xVals = rdd.map(lambda ray: ray[:,0])
        self._minX = xVals.map(lambda arr: arr.min()).min()
        self._maxX = xVals.map(lambda arr: arr.max()).max()
        self._num_partitions = num_partitions or rdd.getNumPartitions()
        self._rangeX = self._maxX - self._minX
        self._partitionWidth = self._rangeX/self._num_partitions

    @property
    def num_partitions(self):
        return self._num_partitions

    def hash_function(self,pixel):
        return int((pixel - self._minX)/self._partitionWidth)

    def relevant_partitions(self,pixel,radius):
        part1 = self.hash_function(pixel)
        part2 = self.hash_function(pixel-radius)
        part3 = self.hash_function(pixel+radius)
        return list(set(part1,part2,part3))
