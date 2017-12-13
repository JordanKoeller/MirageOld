# Lensing Simulator

### Jordan Koeller

This build uses Spark to perform the large computations involved on a cluster.

The code can be found inside the spark_impl directory. To call the code,
python uses the pyspark interface to interract with the JVM. These calls on
the JVM can be found in src/Calculator/Engine/Engine_ScalaSpark.py. Once inside 
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




