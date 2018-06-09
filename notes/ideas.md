For Spark interraction - create a decorator that takes a function or object with an `operator()` method and returns an object/decorator suitable for running in a spark stream

mark each ray with where on the disk it intersected the quasar. And then for each pixel in a magmap, include that information in a third dimension of the array. 
	Maybe this can be described with coefficients of a gaussian distribution or something, rather than ennumerating each ray? Will need to investigate
	Another way would be to save coefficients for the first few terms in a Fourier series or a Fourier space. See JPG image compression formatting for ideas.

Once pixels are marked, can then have it combine those data with a magnification map to calculate the MagMap at any arbitrary wavelength
	will need a wrapper class for MagMap and LightCurve so you can select what wavelength to investigate.


From the star initial mass function, select a proportion of masses to be in binaries
	Will need to investigate period distributions to find out how to model the binaries accordingly
	Once have random movement of stars, should have the binaries in orbits with their barycentre the randomly moving object

For random star motion, may need to use monopole/dipole/quadrupole/etc moments to describe further away stars for performance.
	Info on this from Joachim's thesis


Use Fermat's principle to find zeros in travel time to locate image locations for matching with real data and modeling systems.


From the correlation between the second derivative of time delay surface and magnification, would it be possible to write a semi-analytic equation that gives magnification with the disk size as one of the parameters?

Interference patterns from time delay through microimages?

\mu_T for a pointLens = 1.34. We see much higher magnification jumps at caustics. \mu_T for a binary lens is closer to 3. For even more intricate caustic networks, could we discern the nature of a caustic by the change in brightness of the image by constrains such as \mu_T, removing some degeneracies?
Similarly, Time of the caustic event is invariant for a point lens, so by looking at the time it takes to cross we can characterize the caustic further?

Maybe a way to break degeneracy is with a fourier transform of the light curve? Analogously to how the signal of a NMR signal fourier transformed gives insight into the unique environments of electrons around hydrogen atoms?


