from astropy import units as u

class SpecialUnitsList(list):
	"""A special list for lists of instances of `astropy.unit` instances. Provides a method to easily
	register all contained units"""
	def __init__(self, *args,**kwargs):
		for arg in args:
			assert isinstance(arg,u.UnitBase)
		super().__init__(args)


	def _checkType(self,elem):
		if isinstance(elem,u.UnitBase):
			return
		else:
			raise ValueError("Argument must be a UnitBase object. To define UnitBase objects, use astropy's def_unit method.")
	
	def append(self,*elems):
		for elem in elems:
			self._checkType(elem)
		for elem in elems:
			super().append(elem)

	def register(self):
		for elem in self:
			u.add_enabled_units(elem)


		