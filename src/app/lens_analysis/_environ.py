def __EventLoopActive():
	from PyQt5 import QtWidgets
	if QtWidgets.QApplication.instance():
		return True
	else:
		return False
def requiresGUI(fn):
	def decorator(*args,**kwargs):
		if __EventLoopActive():
			return fn(*args,**kwargs)
		else:
			print("Must have Qt5 Event Loop initialized. To initialize, run the command \n\n>>> %gui qt5 \n\n")
	return decorator

