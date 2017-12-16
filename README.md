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
observation. In order to understand these systems, however, we must build a computational
model.

To model gravitationally lensed quasars, we ray-trace ~10^8 different paths light can 
take, travelling from the quasar to the observer. Due to the large number of rays traced, this
computation is CPU-intensive as well as memory-intensive. Hence Spark is used to break the
calculation up across a cluster of machines. The final data that we want to produce are magnification
maps (Figure 1). To calculate these maps, we query the data for the number of data points within a given radius
of each pixel. Hence, spatial data structures are crucial to make this operation fast.

### Figure 1: Sample Magnification Map
![alt text][MagMap]

## Analysis & Implimentation

Three stages are involved in performing the calculation. The three stages are ray-tracing, 
repartitioning, and querying. The slowest stage of these three stages is the querying stage.

In Stage 1 (Figure 2), Python hands off the parameters of the system (things like distances, 
masses, positions, etc) to the JVM. Spark then builds an `RDD` of rays to trace, and transforms it
from the observer plane to the source plane based on the gravitational potential of the system,
specified by the parameters. The result of Stage 1 is an `RDD[(XYIntPair,XYDoublePair)]` where
the integer pair is the initial pixel location of the ray, and the resultant location of the
pixel on the source plane after accounting for lensing.
### Figure 2: Grid Query Code Flow
![alt text][Phase1Diagram]

In Stage 2, the `RDD` produced by Stage 1 is shuffled, such that each partition contains data points that
are near each other spatially in a data structure I'm calling an `RDDGrid`. This allows for efficient retrieval of
data points that are near each other spatially with minimal network traffic. Two partitioning
schemes were attempted; equally spaced columns (`ColumnPartitioner`), and columns of varying width to ensure the data
is balanced across the nodes (`BalancedColumnPartitioner`). Performance was best with the `BalancedColumnPartitioner`. 
Within each partition, the data was then organized in a spatial grid (`VectorGrid`) (Figure 2). From here,
the `RDDGrid` is cached and control returns to Python.


Lastly, in Stage 3 (Figure 3), the `RDDGrid` is queried ~10^6 times to visualize the data. Each query is a 
query of how many data points are within a specified radius of the point of interest. Hence, the necessity of the 
spatial grid built in Stage 2. For most query points, this operations is relatively simple. Query points near the 
boundaries of partitions, however, need to be specially handled. If a search area overlaps with more than one partition,
all the partitions need to be queried for data around that point, and then those sets of returned data points unioned 
for the complete set of relevant data points. To make querying faster, before querying the `RDDGrid`, the query points
were partitioned with the same scheme the data points were partioned by. Hence, partitions do not need to search for
superflous query points nowhere near that section of the data. However, this partitioning of data points produces
duplicates of query points for each partition that overlaps with it to prevent the boundary issue described above.
### Figure 3: Grid Query Code Flow
![alt text][Phase3Diagram]

After querying is finished, the returned `Array[Array[Int]]` representing monochromatic pixel values for the magnification map
is written to a temporary file, to be loaded in by Python after the JVM is exited for further processing and scaling of the data.

## Discussion

While analyzing the problem, I quickly realized that the interesting part of breaking spatial data across a cluster has
to do with partitioning the data, and how to query it. For partitioning the data, there are two primary considerations.
The first one is how to balance the data across the partitions. To account for different densities in different regions
of the data, the `BalancedColumnPartitioner` was ideal from a memory standpoint, as it ensures that there is an
approximately equal amount of data in each partition. However, for the question I am asking, this does have some
drawbacks. In Stage 3, the points queried are evenly spaced across the dataset. Hence, having partitions of different 
areas leads to an imbalance in how much work each partition must do. In the future I will be adding some tolerance 
to imbalance between partitions, to help keep the area covered by each partition more uniform. 

Another partitioner I will be trying in the future is one based on a kD-Tree algorithm. The advantage of this partitioner
is it allows more fine-grained tuning of the data structure to the densities of the data. Hence, it should allow for faster
queries of the data with more uniform data density within each partition. When designing this, I may also allow for 
minor imbalances to form, to help keep the area covered by each partition more uniform.

The second consideration is how to handle queries of data on the boundaries of partitions. To reduce network traffic,
I decided to pre-process the query points, such that each partition queries any point that overlaps at all with it.
Finally, the set of data points returned from each query point are aggregated for the final set of returned data points.
Alternatively, I considered copying the data near each partition boundary onto both sides of the boundary. While this would 
be ideal for data that needs to communicate with each other, this was not necessary for my calculation.

### Figure 4: Zoom-in of Error in Map Calculation
![alt text][MagMapError]

In summary, Spark seems promising for speeding up my simulation by a significant factor. The only reason I say it 
is not successful yet is because of a slight bug with merging data across partitions, leading to straight lines 
cutting through magnification maps (Figure 4). Before Spark, I was running
the program locally, using an implimentation written in C with openmp for parallelization. Comparing the performance
of the two versions, for similarly-sized datasets, the Spark implimentation affords almost an order of magnitude speedup.
Further optimization may be possible by taking advantage of practices for fast Scala code. 


## References

see `references.png`

[Phase1Diagram]:https://github.com/JordanKoeller/lensing_simulator/blob/master/diagrams/phase1_diagram.png
[Phase3Diagram]:https://github.com/JordanKoeller/lensing_simulator/blob/master/diagrams/phase3_diagram.png
[MagMap]:https://github.com/JordanKoeller/lensing_simulator/blob/master/diagrams/trippymagmap.png
[MagMapError]:https://github.com/JordanKoeller/lensing_simulator/blob/master/diagrams/hiResCropped.png
[partitionHistogram]:https://github.com/JordanKoeller/lensing_simulator/blob/master/diagrams/partitioningHistogram.png
