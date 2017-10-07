print("Initialized")
from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if rank == 0:
	from app.Utility.MPISignals import *
	counter = 0
	while counter < 100:
		time.sleep(1)
		counter += 1
		sendString("String "+str(counter)+"Sent to 1",ProcessRole.CALCULATION_PROCESS)
		sendString("String "+str(-counter*2)+"Sent to 2",ProcessRole.RECORD_PROCESS)

elif rank == 1:
	from app.Utility.MPISignals import *
	print("Rank 1 Reporting")
	listener = MPIListener()	
	listener.listenFor(ProcessRole.MAIN_PROCESS)
	listener.listenFor(ProcessRole.RECORD_PROCESS,tag=SignalCode.BUFFER_SPECS)
elif rank == 2:
	from app.Utility.MPISignals import *
	print("Rank 2 Reporting")
	listener = MPIListener()	
	listener.listenFor(ProcessRole.MAIN_PROCESS)
	counter = 0
	data = np.ndarray((10000,10000))
	while counter < 100:
		sendContiguousArray((data+45),ProcessRole.CALCULATION_PROCESS)
		time.sleep(1)
		counter += 1
		# sendString(str(data) + "From 3",ProcessRole.CALCULATION_PROCESS)
