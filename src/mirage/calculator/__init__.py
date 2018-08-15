import os


from .ExperimentTableRunner import ExperimentTableRunner
from .StarGenerator import StationaryStarGenerator, getMassFunction
currDir = os.path.abspath(__file__)[0:-11]
gpu_kernel = open(currDir+'ray_tracer.cl')



        


#Fully Documented package