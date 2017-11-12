from __future__ import division

from .Engine import Engine

from ...Utility.PointerGrid import PointerGrid


class Engine_Spark(object):
	"""Engine Implimentation, meant to be ran on a spark cluster."""

	_parameters = None
	_preCalculating = False
	_trueLuminsoity = 1.0
	_core_count = 1

	def __init__(self):
		super(Engine_Spark, self).__init__()
		from app.Preferences import GlobalPreferences
		self._core_count = GlobalPreferences['core_count']


	def ray_trace(self,*args,**kwargs):
		'''
		Ray trace the lensed system. returns an RDD[(Double,Double,Double,Double)]

		'''


	# def 