def DrawerFactory(drawImage = True, drawCurve = False):
	if drawImage and drawCurve:
		return CompositeDrawer(ImageDrawer(),CurveDrawer())
	elif drawImage:
		return ImageDrawer()
	else:
		return CurveDrawer()