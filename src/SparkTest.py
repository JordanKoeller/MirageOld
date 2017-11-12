from pyspark import SparkContext, SparkConf
from app.Utility.PointerGrid import PointerGrid
def calculator(elem):
	'''
	Should be a double? Then mutate it and return.
	'''

	return (elem+2)**2

class SparkTest(object):
	"""Test I can do what I need with Spar"""
	def __init__(self):
		super(SparkTest, self).__init__()
		conf = SparkConf().setAppName("PySpark API Test")
		conf = (conf.setMaster('local[4]')
		        .set('spark.executor.memory', '3G')
		        .set('spark.driver.memory', '3G'))
		        # .set('spark.driver.maxResultSize', '10G'))
		self._sc = SparkContext(conf=conf)
		self._sc.setLogLevel("WARN")


	def run_test(self):
		import numpy as np 
		dataX = np.ndarray((2000,2000))
		dataY = np.ndarray((2000,2000))
		rddData = self._sc.parallelize(data)
		grid = PointerGrid(dataX.data,dataY.data,2000,2000,2000)
		print("Made the data into an RDD")
		print(str(rddData.take(5)))
		mutated = rddData.map(calculator)
		print("Finished caclulating")
		print(str(mutated.take(5)))


if __name__ == "__main__":
	test = SparkTest()
	test.run_test()
	test._sc.close()
