from .LightCurve import LightCurve, LightCurveBatch
from .LightCurve import LightCurveClassificationTable
from .peak_finding import isolate_events


def maximum_curve_length(distance):
    from mirage.preferences import GlobalPreferences
    from mirage.utility import QuantityJSONDecoder
    from astropy import units as u
    qd = QuantityJSONDecoder()
    timescale = qd.decode(GlobalPreferences['light_curve_parameters']['maximum_timescale'])
    qv = qd.decode(GlobalPreferences['light_curve_parameters']['maximum_quasar_velocity'])
    dtheta = qv.to('m/s')*timescale.to('s')/distance.to('m')
    ret = u.Quantity(dtheta.value,'rad')
    print(ret.to("uas"))
    print(ret)
    return ret