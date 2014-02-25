def WithExpiry(proto = None,expiry = None): 
    from marketsim.gen._out._ifunction import IFunctionIObservableIOrderIFunctionfloat
    from marketsim.gen._out._ifunction import IFunctionfloat
    from marketsim.gen._out.order._curried._volume_withexpiry import volume_WithExpiry_FloatIObservableIOrderFloat as _order__curried_volume_WithExpiry_FloatIObservableIOrderFloat
    from marketsim import rtti
    if proto is None or rtti.can_be_casted(proto, IFunctionIObservableIOrderIFunctionfloat):
        if expiry is None or rtti.can_be_casted(expiry, IFunctionfloat):
            return _order__curried_volume_WithExpiry_FloatIObservableIOrderFloat(proto,expiry)
    raise Exception('Cannot find suitable overload for WithExpiry('+str(proto) +':'+ str(type(proto))+','+str(expiry) +':'+ str(type(expiry))+')')
