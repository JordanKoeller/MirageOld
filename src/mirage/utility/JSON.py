from abc import ABC, abstractmethod, abstractproperty, abstractclassmethod


class JSONable(ABC):
	"""Abstract base class for objects that have methods for converting to and from
	JSON representations."""
	def __init__(self):
		super(JSONable, self).__init__()

	@abstractproperty
	def json(self):
		pass

	@abstractclassmethod
	def from_json(cls,js):
		pass
		

	#Method template



	# @property 
	# def json(self):

	# @classmethod
	# def from_json(cls,js):
