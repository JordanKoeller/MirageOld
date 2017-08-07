

class UserInputParser(object):
	"""Provides an interface for constructing and parsing objects specified by user input.

	Has two important methods: buildObject and bindFields.

	Parameters:

	view : view inheriting from Views.View class.

	Methods:

	def buildObject():
		parses the fields within the view assigned upon initialization to construct the 
		appropriate object. Returns the fully constructed object.

	def bindFields(obj):
		Reads obj's attributes, and fills in the fields contained within the view assigned upon 
		initialization. 

	TO SUBCLASS:

	UserInputParser has two abstract methods that must be overwritten. _buildObjectHelper and
	_bindFieldsHelper, which are what are called by buildObject and bindFields, respectively.

	UserInputParsers should only be interracted with by the non-helper functions, as they provide
	proper exception handling systems."""
	def __init__(self, view):
		self.view = view

	def buildObject(self,*args,**kwargs):
		"""Parses self.view to construct and return the object appropriate for this UserInputParser
		subclass and instance.

		Provides exception handling, where if a exception is thrown the message is printed, sent to
		the GUI messageBar, and None is returned. 

		*args and **kwargs are passed onto this methods helper function"""
		try:
			return self._buildObjectHelper(*args,**kwargs)
		except:
			return None 

	def bindFields(self,obj,*args,**kwargs):
		"""Parses obj's attributes, and sets self.view's fields to reflect them.

		Provides exception handling, where if a exception is thrown the message is printed, sent to
		the GUI messageBar, and None is returned. 

		*args and **kwargs are passed onto this methods helper function"""
		try:
			return self._bindFieldsHelper(obj,*args,**kwargs)
		except:
			return None 

        # except (AttributeError, ValueError) as e:
        #     self.view.signals['progressLabel'].emit("Error. Input could not be parsed to numbers.")
        #     print(str(e))
        #     return None
        # except ParametersError as e:
        #     self.view.signals['progressLabel'].emit(e.value)
        #     print(str(e))
        #     return None
        # except SyntaxError as e:
        #     print(str(e))
        #     self.view.signals['progressLabel'].emit("Syntax error found in trial variance code block.")
        #     return None

	def _buildObjectHelper(self,*args,**kwargs):
		'''Abstract method to be overwritten with the code specifying how to build the object 
		from self.view.'''
		pass

	def _bindFieldsHelper(self,obj,*args,**kwargs):
		'''Abstract method to be overwritten with the code specifying how to sift through obj's
		attributes and have self.view reflect them.'''
		pass
		