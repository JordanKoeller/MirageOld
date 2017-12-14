# Lensing Simulator

### Jordan Koeller

This build uses Spark to perform the large computations involved on a cluster.

The code can be found inside the `spark_impl` directory. To call the code,
python uses the pyspark interface to interract with the JVM. These calls on
the JVM can be found in `src/app/Calculator/Engine/Engine_ScalaSpark.py`. Once inside 
the JVM, all calculation occurs there and then writes the result to temporary 
file. Python may then open the file to fetch the data and continue to interract
with it.

## Problem Description

By studying gravitationally lensed quasars, astrophysicists have the potential to learn 
about dark matter distributions in the universe along with the size and composition
of distant quasars to orders of magnitude of higher precision than through direct
observation (1). In order to understand these systems, however, we must build a computational
model.

To model gravitationally lensed quasars, we ray-trace 10^8 to 10^9 different paths light can 
take, travelling from the quasar to the observer. Due to the large number of rays traced, this
computation is CPU-intensive as well as memory-intensive. Hence, Spark is used to break the
calculation up across a cluster of machines.

## Analysis

Three stages are involved in performing the calculation. The three stages are ray-tracing, 
repartitioning, and querying. The slowest stage of these three stages is the querying stage.

In Stage 1 (Figure 1), Python hands off the parameters of the system (things like distances, 
masses, positions, etc) to the JVM. Spark then builds an `RDD` of rays to trace, and transforms it
from the observer plane to the source plane based on the gravitational potential of the system,
specified by the parameters. The result of Stage 1 is an `RDD[(XYIntPair), (XYDoublePair)]` where
the integer pair is the initial pixel location of the ray, and the resultant location of the
pixel on the source plane after accounting for lensing.

In Stage 2, the `RDD` produced by Stage 1 is shuffled, such that each partition contains data points that
are near each other spatially in a data structure I'm calling an `RDDGrid`. This allows for efficient retrieval of
data points that are near each other spatially with minimal network traffic. Two partitioning
schemes were attempted; equally spaced columns (`ColumnPartitioner`), and columns of varying width to ensure the data
is balanced across the nodes (`BalancedColumnPartitioner`). Performance was best with the `BalancedColumnPartitioner`. 
Within each partition, the data was then organized in a spatial grid (`VectorGrid`). From here,
the `RDDGrid` is cached and control returns to Python.

Lastly, in Stage 3 (Figure 2), the `RDDGrid` is queried ~10^6 times to visualize the data. Each query is a 
query of how many data points are within a specified radius of the point of interest. Hence, the necessity of the 
spatial grid built in Stage 2. For most query points, this operations is relatively simple. Query points near the 
boundaries of partitions, however, need to be specially handled. If a search area overlaps with more than one partition,
all the partitions need to be queried for data around that point, and then those sets of returned data points unioned 
for the complete set of relevant data points. To make querying faster, before querying the `RDDGrid`, the query points
were partitioned with the same scheme the data points were partioned by. Hence, partitions do not need to search for
superflous query points nowhere near that section of the data. However, this partitioning of data points produces
duplicates of query points for each partition that overlaps with it to prevent the boundary issue described above.





