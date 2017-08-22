Enclosed are 3 numpy arrays, with data for light curves of a specific caustic crossing.

The model simulated is image C from QSO 2237+0305. 100% of the mass is calculated as stars.
The starfield calculated is of size 393x393 uarcsecs, traced by 10000x10000 rays.
The magnification map is of size 98x98 uarcsecs, at the center of the starfield.

The three light curves come from four different quasar sizes. They model quasars of:
- 10 gravitational radii
- 20 gravitational radii
- 40 gravitational radii

where the mass of the supermassive black hole is set as 1 billion solar masses.

I tried to calculate a 5 gravitational radii object, but due to the small number of rays traced it was a very noisy light curve. In one of the images is a blue light curve, and that shows what the 5 R_g data looked like.



TO OPEN THE FILES:

start up a python REPL and run the following commands:

>>> import numpy as np
>>> data = np.load('lightCurveData')
>>> x = data['xAxis']
>>> y = data['KEYCODE']

The KEYCODEs allowed are "10R_g", "20R_g", and "40R_g", which correspond to simulated quasars of size 10, 20, and 40 gravitational radii, respectively. The Variable X is just a numpy array counting from 0 to 71, which is the number of data points collected. This correlates to distance traveled by the quasar, though at an unknown factor. Again, I've been refactoring a bunch and I'll have that information and send it when I can retrieve it again.



To go to magnitude, the easiest would be with

>>> y = -2.5*np.log10(y)

To plot, I would recommend the following:

>>> from matplotlib import pyplot as pl
>>> pl.plot(x,y,label=str(Quasar SIZE))
>>> pl.legend()
>>> pl.show()

If you have any questions let me know! Again, this data set is very much a work in progress but it has a lot of the features I was looking for when trying to find good caustics so I thought I would send it anyway.


Jordan

