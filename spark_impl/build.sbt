val fastutil = "it.unimi.dsi" % "fastutil" % "8.1.1"
val scalafx = "org.scalafx" % "scalafx_2.11" % "8.0.102-R11"// % "provided"
val spark = "org.apache.spark" % "spark-core_2.11" % "2.2.0" % "provided"
val sparkSQL = "org.apache.spark" % "spark-sql_2.11" % "2.2.0" % "provided"
val mllib = "org.apache.spark" % "spark-mllib_2.11" % "2.2.0" % "provided"
lazy val root = (project in file("."))
  .settings(
    name         := "lensing_simulator_spark_kernel",
    organization := "edu.trinity",
    scalaVersion := "2.11.8",
    version      := "0.1.0-SNAPSHOT",
    libraryDependencies += spark
//    libraryDependencies += fastutil

  )
