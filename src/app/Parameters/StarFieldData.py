

class StarFieldData(object):
	"""docstring for StarFieldData"""
	def __init__(self):
		super(StarFieldData, self).__init__()
		
	@property
	def keyword(self):
		return "starfield"

	@property
	def jsonString(self):
		return '[]'
		
	def __str__(self):
		return ""