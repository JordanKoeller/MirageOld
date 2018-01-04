from .Engine cimport Engine




cdef class Engine_Spark(Engine):
    '''
    Class for ray-tracing and getting magnification maps from the cluster. Similar to the Engine class but for parallel execution.
    '''

    cdef rays
    cdef _sparkContext
