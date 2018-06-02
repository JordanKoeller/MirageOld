
cd ../src
export PYSPARK_DRIVER_PYTHON=ipython

#Pull out the configuration variables
MASTER=$(python -c 'from app.preferences import GlobalPreferences; print(GlobalPreferences["spark_configuration"]["master"])')
DRIVER_MEMORY=$(python -c 'from app.preferences import GlobalPreferences; print(GlobalPreferences["spark_configuration"]["driver-memory"])')
EXECUTOR_MEMORY=$(python -c 'from app.preferences import GlobalPreferences; print(GlobalPreferences["spark_configuration"]["executor-memory"])')
EXTRA_ARGS=$(python -c 'from app.preferences import GlobalPreferences; print(GlobalPreferences["spark_configuration"]["command-line-args"])')
JAR_LOC='../spark_impl/target/scala-2.11/lensing_simulator_spark_kernel-assembly-0.1.0-SNAPSHOT.jar'


#The command itself
pyspark --master $MASTER --executor-memory $EXECUTOR_MEMORY --driver-memory $DRIVER_MEMORY --jars $JAR_LOC
