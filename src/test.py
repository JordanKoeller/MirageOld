from app.Utility.MPISignals import *

from mpi4py import MPI
import numpy as np
import time
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
listener = MPIListener()	
if rank == 0:
	counter = 0
	while True:
		counter += 1
		print("SEND A MESSAGE")
		sendString("String "+str(counter)+"Sent to 1",ProcessRole.CALCULATION_PROCESS)
		sendString("String "+str(-counter*2)+"Sent to 2",ProcessRole.RECORD_PROCESS)
		time.sleep(1)

elif rank == 1:
	listener = MPIListener()	
	listener.listenFor(ProcessRole.MAIN_PROCESS)
	# listener._listenerThread.start()
	listener.listenLoop()
elif rank == 2:
	listener = MPIListener()	
	listener.listenFor(ProcessRole.MAIN_PROCESS)
	listener.listenLoop()
	# listener._listenerThread.start()
