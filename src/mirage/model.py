
from mirage.engine import Engine, Engine_PointerGrid, Engine_ScalaSpark, Engine_MagMap
from mirage.utility import Vector2D
from mirage.parameters import DefaultParameters

class AbstractModel(object):
    
    
    def __init__(self,simulation,engine):
        self._simulation = simulation
        self._engine = engine


    def set_simulation(self,simulation):
        self._simulation = simulation

    def bind_simulation(self):
        self._engine.update_parameters(self.parameters)

    def regenerate_stars(self):
        try:
            self.parameters.regenerate_stars()
            self.bind_parameters()
        except:
            print("Failed to regenerate stars")

    def get_raw_magnification(self):
        if self.parameters.raw_magnification:
            return self.parameters.raw_magnification
        else:
            return self.engine.calculate_raw_magnification()

    @property
    def simulation(self):
        return self._simulation
    

    @property
    def parameters(self):
        return self.simulation.parameters

    @property
    def engine(self):
        return self._engine

    @property
    def experiments(self):
        return self.simulation.experiments

    def disable(self):
        pass


class ParametersModel(AbstractModel):
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
        AbstractModel.__init__(self, parameters, engine)

    @classmethod
    def fromSubClass(cls,instance):
        '''
        Convert a :class:`AbstractModel` subtype instance to a :class:`ParametersModel` object instance. 
        '''
        assert isinstance(instance,AbstractModel)
        p = instance.parameters
        return cls(p)

    def zoom_to(self,center,dims):
        #We assume the square selected is a perfect square.
        old_canvDim = self.parameters.canvasDim
        old_dTheta = self.parameters.dTheta
        canvDimRatio = dims.x/old_canvDim
        new_dTheta = old_dTheta*canvDimRatio*old_canvDim
        old_center = self.parameters.galaxy.center
        center_p = center - Vector2D(old_canvDim/2,old_canvDim/2)
        center_angle = center_p*old_dTheta.to('rad').value
        center_angle = center_angle.setUnit('rad')
        new_center = old_center.to('rad') - center_angle.to('rad')

        # center = self.parameters.pixelToAngle(center)
        newP = self.parameters.copy()
        newP.galaxy.update(center=new_center)
        print("Center of galaxy at " + str(new_center.to('arcsec')))
        newP.update(dTheta = new_dTheta)
        return newP


        
        
class TrialModel(AbstractModel):
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
        AbstractModel.__init__(self, parameters, engine)
        
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

        
        
class ClusterModel(AbstractModel):

    def __init__(self, simulation):
        engine = Engine_ScalaSpark()
        AbstractModel.__init__(self, simulation, engine)
        
class CPUModel(AbstractModel):
    
    def __init__(self,simulation):
        engine = Engine_PointerGrid()
        AbstractModel.__init__(self, simulation, engine)
       
def __initialize():
    from mirage.preferences import GlobalPreferences
    global CalculationModel
    if GlobalPreferences['calculation_device'] == 'cpu':
        CalculationModel = CPUModel
    if GlobalPreferences['calculation_device'] == 'spark':
        CalculationModel = ClusterModel

CalculationModel = None
__initialize()
