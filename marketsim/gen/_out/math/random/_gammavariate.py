from marketsim import registry
from marketsim import float
from marketsim.ops._function import Function
from marketsim import float
from marketsim import float
@registry.expose(["Random", "gammavariate"])
class gammavariate(Function[float]):
    """ 
      Conditions on the parameters are |alpha| > 0 and |beta| > 0.
    
      The probability distribution function is: ::
    
                   x ** (alpha - 1) * math.exp(-x / beta)
         pdf(x) =  --------------------------------------
                      math.gamma(alpha) * beta ** alpha
    """ 
    def __init__(self, Alpha = None, Beta = None):
        from marketsim import rtti
        self.Alpha = Alpha if Alpha is not None else 1.0
        self.Beta = Beta if Beta is not None else 1.0
        rtti.check_fields(self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'Alpha' : float,
        'Beta' : float
    }
    def __repr__(self):
        return "gammavariate(%(Alpha)s, %(Beta)s)" % self.__dict__
    
    def __call__(self, *args, **kwargs):
        import random
        return random.gammavariate(self.Alpha, self.Beta)
    
    def _casts_to(self, dst):
        return gammavariate._types[0]._casts_to(dst)
    
gammavariate = gammavariate
