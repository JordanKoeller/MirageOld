print("Got HEre")
from app.Utility.MPISignals import *

from mpi4py import MPI
import numpy as np
comm = MPI.COMM_WORLD

# print(ProcessRole(comm.Get_rank()))
# print(comm.Get_rank())
if comm.Get_rank() == 0:
	data = np.ndarray((200,200))
	# sendContiguousArray(data,ProcessRole.CALCULATION_PROCESS)
elif comm.Get_rank() == 1:
	# data = comm.recv(source=ProcessRole.MAIN_PROCESS.value,tag=SignalCode.DEFAULT.value)
	print("Received Data")
	# sendSignal(ProcessRole.RECORD_PROCESS,SignalCode.START)
elif comm.Get_rank() == 2:
	data = comm.recv(ProcessRole.CALCULATION_PROCESS.value,tag=SignalCode.START.value)
	print("Done on com 2")

