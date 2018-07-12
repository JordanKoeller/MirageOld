
from mirage.engine import Engine, Engine_PointerGrid, Engine_ScalaSpark, Engine_MagMap
from mirage.parameters import Parameters, DefaultParameters


class _AbstractModel(object):
    
    _parameters = None
    _engine = None
    
    def __init__(self,parameters,engine):
        assert isinstance(parameters,Parameters)
        assert isinstance(engine, Engine) or isinstance(engine, Engine_ScalaSpark)
        self._parameters = parameters
        self._engine = engine

    def set_parameters(self, parameters):
        assert isinstance(parameters, Parameters)
        self._parameters = parameters

    def bind_parameters(self):
        self._engine.update_parameters(self._parameters)

    def regenerate_stars(self):
        try:
            print(self._parameters.galaxy.percentStars)
            self._parameters.regenerateStars()
            self.bind_parameters()
        except:
            print("Failed to regenerate stars")


    @property
    def parameters(self):
        return self._parameters

    @property
    def engine(self):
        return self._engine

    def disable(self):
        pass


class ParametersModel(_AbstractModel):
    '''
    Standard Model for calculating lensed systems from a system description.

    Parameters:
    
    - `parameters` (:class:`mirage.parameters.Parameters`) : System description to build the model around.
    - `engine` (:class:`mirage.engine.Engine`) : Engine to use for calculating the system. By default, uses a :class:`mirage.calculator.engine.Engine_PointerGrid` for calculating locally.

    '''

    def __init__(self, parameters=DefaultParameters(),
                 engine=Engine_PointerGrid()):
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
    Model for calculating lensed systems from a :class:`mirage.lens_analysis.Trial` instance, or a filename and trial number. To pull data from a file, call the :class:`TrialModel.fromFile` method.
    
    Parameters:
    
    - `trial` (:class:`mirage.lens_analysis.Trial`) : Trial containing all the information to describe the system.
     
    '''
        
    def __init__(self,trial):
        from mirage.lens_analysis import Trial
        assert isinstance(trial,Trial)
        parameters = trial.parameters
        self._trial = trial
        magmap = self._trial.magMap
        mmp = self._trial.parameters.extras['magmap']
        params = self._trial.parameters
        engine = Engine_MagMap(params,mmp,magmap)
        _AbstractModel.__init__(self, parameters, engine)
        
    @classmethod
    def fromFile(cls,filename,trialnumber):
        '''
        Convenience function for building a TrialModel straight from file. This is equivalent to calling 
        >>> from mirage import lens_analysis
        >>> data = lens_analysis.load(filename)
        >>> trial = data[trialnumber]
        >>> TrialModel(trial)
        '''
        from mirage import lens_analysis
        trial = lens_analysis.load(filename)
        return cls(trial[trialnumber])
    
    @property
    def magnification_map(self):
        return self._trial.magMap
    

    def specify_light_curve(self,start,end):
        if not 'lightcurve' in self.parameters.extras:
            from mirage.parameters.ExperimentParams import LightCurveParameters
            self.parameters.extras.append(LightCurveParameters(start,end,100))
        start = self.parameters.extras['magmap'].pixelToAngle(start)
        end = self.parameters.extras['magmap'].pixelToAngle(end)
        self.parameters.extras['lightcurve'].update(start = start, end = end)

        
        
class ClusterModel(_AbstractModel):

    def __init__(self, parameters):
        engine = Engine_ScalaSpark()
        _AbstractModel.__init__(self, parameters, engine)
        
class CPUModel(_AbstractModel):
    
    def __init__(self,parameters):
        engine = Engine_PointerGrid()
        _AbstractModel.__init__(self, parameters, engine)
       
def __initialize():
    from mirage.preferences import GlobalPreferences
    global CalculationModel
    if GlobalPreferences['calculation_device'] == 'cpu':
        CalculationModel = CPUModel
    if GlobalPreferences['calculation_device'] == 'spark':
        CalculationModel = ClusterModel

CalculationModel = None
__initialize()