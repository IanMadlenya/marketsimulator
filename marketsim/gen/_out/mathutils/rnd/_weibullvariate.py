from marketsim import registry, types, ops
import random

@registry.expose(['Random', 'Weibull distribution'])
class weibullvariate(ops.Function[float]):
    """ 
    """ 
    def __init__(self, Alpha = None, Beta = None):
        self.Alpha = Alpha if Alpha is not None else 1.0
        self.Beta = Beta if Beta is not None else 1.0

    @property
    def label(self):
        return repr(self)

    _properties = {
        'Alpha' : float,
        'Beta' : float
    }

    def __repr__(self):
        return "weibullvariate(Alpha = "+repr(self.Alpha)+" , Beta = "+repr(self.Beta)+" )" 


    def __call__(self, *args, **kwargs):
        return random.weibullvariate(self.Alpha, self.Beta)

    def _casts_to(self, dst):
        return weibullvariate._types[0]._casts_to(dst)



