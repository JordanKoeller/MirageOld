
from app.engine import Engine, Engine_PointerGrid, Engine_MagMap
from app.parameters import Parameters, DefaultParameters


class _AbstractModel(object):
    
    _parameters = None
    _engine = None
    
    def __init__(self,parameters,engine):
        assert isinstance(parameters,Parameters)
        assert isinstance(engine, Engine)
        self._parameters = parameters
        self._engine = engine
        
        
    def setParameters(self,parameters):
        assert isinstance(parameters, Parameters)
        self._parameters = parameters
        self._engine.updateParameters(self._parameters)
    
    @property
    def parameters(self):
        return self._parameters
    

    @property
    def engine(self):
        return self._engine
    
    
    
    
class ParametersModel(_AbstractModel):
    '''
    Standard Model for calculating lensed systems from a system description.
    
    Parameters:
    
    - `parameters` (:class:`app.parameters.Parameters`) : System description to build the model around.
    - `engine` (:class:`app.engine.Engine`) : Engine to use for calculating the system. By default, uses a :class:`app.calculator.engine.Engine_PointerGrid` for calculating locally.
    
    '''


    def __init__(self, parameters = DefaultParameters, engine = Engine_PointerGrid()):
        '''
        Constructor
        '''
        _AbstractModel.__init__(self, parameters, engine)
        
    @classmethod
    def fromSubClass(cls,instance):
        '''
        Convert a :class:`AbstractModel` subtype instance to a :class:`ParametersModel` object instance. 
        '''
        assert isinstance(instance,_AbstractModel)
        p = instance.parameters
        return cls(p)
        
        
class TrialModel(_AbstractModel):
    '''
    Model for calculating lensed systems from a :class:`app.lens_analysis.Trial` instance, or a filename and trial number. To pull data from a file, call the :class:`TrialModel.fromFile` method.
    
    Parameters:
    
    - `trial` (:class:`app.lens_analysis.Trial`) : Trial containing all the information to describe the system.
     
    '''
        
    def __init__(self,trial):
        from app.lens_analysis import Trial
        assert isinstance(trial,Trial)
        parameters = trial.parameters
        engine = Engine_MagMap()
        _AbstractModel.__init__(self, parameters, engine)
        
    @classmethod
    def fromFile(cls,filename,trialnumber):
        '''
        Convenience function for building a TrialModel straight from file. This is equivalent to calling 
        >>> from app import lens_analysis
        >>> data = lens_analysis.load(filename)
        >>> trial = data[trialnumber]
        >>> TrialModel(trial)
        '''
        from app import lens_analysis
        trial = lens_analysis.load(filename)
        return cls(trial[trialnumber])
        