import os


currDir = os.path.abspath(__file__)[0:-11]
print(currDir+'ray_tracer.cl')
gpu_kernel = open(currDir+'ray_tracer.cl')

#Fully Documented package