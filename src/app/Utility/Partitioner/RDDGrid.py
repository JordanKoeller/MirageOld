import numpy as np

class RDDGrid(object):
        
    def __init__(self,partitioner, spatial_structure_constructor):
        self._partitioner = partitioner
        self._spatial_structure_constructor = spatial_structure_constructor

    def construct(self,rdd):
        self._rdd = self._construct_grid(rdd)
        self._rdd.cache()
                                            
    def _construct_grid(self,rdd):
        partitioned = self._partitioner.partition(rdd)
        partitioned = partitioned.cache()
        ret = partitioned.map(lambda arr:self._spatial_structure_constructor(arr), preservesPartitioning = True)
        return ret


    def query_points(self,points,radius,spark_context):
        '''
        Given an array of locations to query and a radius, returns an array that is the number of data points inside the RDDGrid that fall within the given radius of each element in the passed-in array. In other words, this function maps from a collection of locations to the number of data points within the given radius of each location.
        
        This function is built on top of an RDD, and hence performs all these queries in parallel across a cluster.

        Parameters:
        - `points` (`array_like`) The collection of (x,y) tuples to query.
        - `radius` (:class:`float`) The radius to search for points surrounding each element of the `points` array.

        Returns: `array_like` representing the number of data points found within `radius` of each element in `points`.
        '''
        print("WE ARENT GETTING HERE RIGHT!?")
        #Validate user input
        if not isinstance(np.ndarray,points):
            points = np.array(points)
        assert(points.ndim == 2 and points.shape[1] == 2)

        #Break up the points to query into partitions
        pnts_with_partitions = map(lambda index, pixel: (index, pixel,self._paritioner.relevant_partitions(pixel,radius),np.ndenumerate(points)))
        partition_list = [[] for i in range(0,self._partitioner.num_partitions)]
        for index,pixel, partitions in pnts_with_partitions:
            for partition in partitions:
                partition_list.append(pixel+index)
        partition_npArrays = list(map(lambda arr:np.ascontiguousarray(arr),partition_list))
        broadcasted_pnts = spark_context.broadcast(partition_npArrays)
        #Now that partitions are done, need to send each partition to the correct rdd partition

        def _query_function(partitionNum,gridIter):
            grid = next(gridIter)
            pixelInd = broadcasted_pnts.value[partitionNum]
            return map(lambda pixel: ([pixel[2],pixel[3]],grid.query_point_count(pixel[0],pixel[1],radius)),pixelInd)


        partition_counts = self._rdd.mapPartitionsWithIndex(_query_function)
        counts = partition_counts.foldByKey(0,lambda x,y:x+y)
        count_array = np.copy(points)
        found_mags = counts.collect()

        for pixel,mag in found_mags:
            count_array[pixel[0],pixel[1]] = mag
        return count_array


