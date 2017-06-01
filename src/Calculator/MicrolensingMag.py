# from matplotlib import pyplot as plt
# from scipy import interpolate
# 
# from Configs import defaultConfigs
# from Configs import microConfigs
# from Calculator.Engine.Engine_cl import Engine_cl
# from Models import defaultGalaxy
# from Models import defaultQuasar
# from Utility import Vector2D
# import astropy.units as u
# import numpy as np


# def configureEngine():
# 	__Engine = Engine_cl(defaultQuasar,defaultGalaxy,defaultConfigs,auto_configure = False)
# 	__Engine.updateConfigs(canvasDim = Vector2D(2000,2000))
# 	__Einstein__Distance = __Engine.einsteinRadius
# 	return (__Engine,__Einstein__Distance)
# 
# print('succesfully imported. Initialization in progress.')
# __Engine, __Einstein__Distance = configureEngine()
# 
# 
# def plotMicroLensing(quasarRadii, xMin=-1.5, xMax=1.5,resolution = 200,smoothing = True):
# 	"""Plots a graph of a microlensed system's magnification coefficient with various quasar radii and distances from the galactic center.
# 	If multiple quasarRadii are passed in, the system will be ran independently for each radius, and all magnifications curves graphed on the same graph.
# 	Parameters:
# 		quasarRadii = list of floats representing the radius of the quasar as a factor of the galaxy's eintein radius.
# 		xMin = float representing the lower xvalue on the graph.
# 		xMax = float representing the upper yvalue on the graph."""

# 	begin = time.clock()
# 	__Engine.updateConfigs(dTheta = __Einstein__Distance*4/__Engine.canvasDim.x)
# 	step = (xMax - xMin)/resolution
# 	xVals = np.arange(xMin,xMax,step)
# 	yVals = xVals.copy()
# 	for quasarRadius in quasarRadii:
# 		for i in range(0,xVals.size):
# 			__Engine.updateQuasar(radius = u.Quantity(quasarRadius*__Einstein__Distance,'rad'))
# 			__Engine.quasar.setPos(Vector2D(xVals[i]*__Einstein__Distance,0.0,'rad'))
# 			yVals[i] = __Engine.getMagnification()
# 		if smoothing:
# 			xNew = np.arange(xMin,xMax,step/(xMax - xMin)/1000)
# 			yNew = np.empty_like(xNew)
# 			tck = interpolate.splrep(xVals,yVals, s = 0)
# 			yNew = interpolate.splev(xNew, tck, der=0)
# 			plt.plot(xNew,yNew,label = "Quasar Radius = " + str(quasarRadius) + " theta_E")
# 		else:
# 			plt.plot(xVals,yVals,label = "Quasar Radius = " + str(quasarRadius) + " theta_E")
# 		print("Line finished")
# 	print("clocked at = " + str(time.clock() - begin) + " seconds")
# 	plt.legend()
# 	plt.xlabel("Distance of quasar from galactic center (theta_E)")
# 	plt.ylabel("Magnification Coefficient")
# 	plt.show()	
# 
# 
# def mag_map(quasarRadius,xMin = -1.5,xMax = 1.5,yMin = -1.5,yMax = 1.5,resolution = 250, smoothing = True):
# 
# 	fig = plt.figure()
# 	ax = fig.add_subplot(111, projection='3d')
# 	xStep = (xMax - xMin)/resolution
# 	yStep = (yMax - yMin)/resolution
# 	xVals = np.arange(xMin,xMax,xStep)
# 	yVals = np.arange(yMin,yMax,yStep)
# 	xVals,yVals = np.meshgrid(xVals,yVals)
# 	zVals = np.empty_like(xVals)
# 	__Engine.updateQuasar(radius = u.Quantity(quasarRadius*__Einstein__Distance,'rad'))
# 	print("Starting plotting")
# 	begin = time.clock()
# 	counter = 0
# 	for i in range(0,xVals.shape[0]):
# 		for j in range(0,yVals.shape[0]):
# 			__Engine.updateQuasar(position = Vector2D(xVals[i,j]*__Einstein__Distance,yVals[i,j]*__Einstein__Distance,'rad'))
# 			zVals[i,j] = __Engine.getMagnification()
# 			if counter % (resolution*resolution/10) == 0:
# 				print("Loading..." + str(counter/(resolution*resolution/100)) + '''%''')
# 			counter += 1
# 	if smoothing:
# 		xNew = np.arange(xMin,xMax,(xMax - xMin)/1000)
# 		yNew = np.arange(yMin,yMax,(yMax - yMin)/1000)
# 		xNew, yNew = np.meshgrid(xNew,yNew)
# 		zNew = np.empty_like(xNew)
# 		tck = interpolate.bisplrep(xVals, yVals, zVals, s=0)
# 		zNew = interpolate.bisplev(xNew[:,0], yNew[0,:], tck)
# 		ax.plot_surface(xNew,yNew,zNew)#label = "Quasar Radius = " + str(quasarRadius) + "theta_E")
# 	else:
# 		ax.plot_surface(xVals,yVals,zVals)#label = "Quasar Radius = " + str(quasarRadius) + "theta_E")
# 	plt.legend()
# 	plt.xlabel("Distance of quasar from galactic center (theta_E)")
# 	plt.ylabel("Magnification Coefficient")
# 	plt.show()