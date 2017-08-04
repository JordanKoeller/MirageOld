
from pyqtgraph.widgets.TableWidget import TableWidget
from PyQt5.Qt import QPushButton, QCheckBox, QTableWidget, QLabel


class ViewTable(QTableWidget):
	"""docstring for ModelTable"""
	def __init__(self, parent=None):
		QTableWidget.__init__(self,parent)
		self._views = []
		self.clearTable()
		self.setColumnCount(4)

	def clearTable(self):
		self._views = []
		headers = ['Name','Type','Enabled','Options']
		self.setColumnWidth(0,100)
		self.setColumnWidth(1,100)
		self.setColumnWidth(2,100)
		self.setColumnWidth(3,100)
		self.horizontalHeader().setStretchLastSection(True)
		self.setHorizontalHeaderLabels(headers)


	def _addView(self,view):
		enabledCheckBox = QCheckBox()
		optionsButton = QPushButton()
		optionsButton.setText("Configure")
		optionsButton.setMinimumWidth(100)
		l1 = QLabel()
		l1.setText(view.title)
		l2 = QLabel()
		l2.setText(view.type)
		self.setRowCount(self.numRows+1)
		row = [l1,l2,enabledCheckBox,optionsButton]
		self._views.append((view,row))

	def setData(self,data):
		for rc in range(len(data)):
			view, row = data[rc]
			for cc in range(len(row)):
				self.setCellWidget(rc,cc,row[cc])

	def loadViews(self,views):
		for view in views:
			self._addView(view)
		self.setData(self._views)

	def selectModel(self,modelID):
		self._selected = modelID
		for rc in range(len(self._views)):
			if self._views[rc][0].modelID == modelID:
				self._views[rc][1][2].setChecked(True)
			else:
				self._views[rc][1][2].setChecked(False)
		# self.clear()
		# print(self._views)
		# self.setData(self._views)

	@property
	def numRows(self):
		return len(self._views)

	@property
	def selectedViews(self):
		ret = []
		for roww in self._views:
			view,row = roww
			if row[2].isChecked():
				ret.append(view)
		return ret 

	@property
	def deselectedViews(self):
		ret = []
		for roww in self._views:
			view,row = roww
			if not row[2].isChecked():
				ret.append(view)
		return ret