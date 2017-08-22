
from astropy import units as u
import json

class QuantityJSONEncoder(object):
	"""docstring for QuantityJSONEncoder"""
	def __init__(self):
		super(QuantityJSONEncoder, self).__init__()
	
	def encode(self, o):
		if isinstance(o,u.Quantity):
			res = {}
			res['unit'] = o.unit.to_string()
			res['value'] = o.value
			return res
		else:
			raise TypeError("Argument o must be an astropy.units.Quantity instance")