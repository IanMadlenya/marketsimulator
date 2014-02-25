from marketsim import registry
from marketsim.gen._out._ifunction import IFunctionIObservableIOrderIFunctionfloat
from marketsim.gen._out._ifunction import IFunctionfloat
@registry.expose(["Order", "WithExpiry"])
class volume_WithExpiry_FloatIObservableIOrderFloat(IFunctionIObservableIOrderIFunctionfloat):
    """ 
     WithExpiry orders can be viewed as ImmediateOrCancel orders
     where cancel order is sent not immediately but after some delay
    """ 
    def __init__(self, proto = None, expiry = None):
        from marketsim.gen._out.order._curried._volume_limit import volume_Limit_SideFloat as _order__curried_volume_Limit_SideFloat
        from marketsim.gen._out._constant import constant_Float as _constant_Float
        from marketsim import rtti
        self.proto = proto if proto is not None else _order__curried_volume_Limit_SideFloat()
        self.expiry = expiry if expiry is not None else _constant_Float(10.0)
        rtti.check_fields(self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'proto' : IFunctionIObservableIOrderIFunctionfloat,
        'expiry' : IFunctionfloat
    }
    def __repr__(self):
        return "WithExpiry(%(proto)s, %(expiry)s)" % self.__dict__
    
    def __call__(self, volume = None):
        from marketsim.gen._out._constant import constant_Float as _constant_Float
        from marketsim.gen._out.order._withexpiry import WithExpiry
        volume = volume if volume is not None else _constant_Float(1.0)
        proto = self.proto
        expiry = self.expiry
        return WithExpiry(proto(volume), expiry)
    
def volume_WithExpiry(proto = None,expiry = None): 
    from marketsim.gen._out._ifunction import IFunctionIObservableIOrderIFunctionfloat
    from marketsim.gen._out._ifunction import IFunctionfloat
    from marketsim import rtti
    if proto is None or rtti.can_be_casted(proto, IFunctionIObservableIOrderIFunctionfloat):
        if expiry is None or rtti.can_be_casted(expiry, IFunctionfloat):
            return volume_WithExpiry_FloatIObservableIOrderFloat(proto,expiry)
    raise Exception('Cannot find suitable overload for volume_WithExpiry('+str(proto) +':'+ str(type(proto))+','+str(expiry) +':'+ str(type(expiry))+')')
