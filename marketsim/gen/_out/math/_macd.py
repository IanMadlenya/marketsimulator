# generated with class generator.python.constructor$Import
from marketsim import registry
from marketsim.gen._out._iobservable._iobservablefloat import IObservablefloat
@registry.expose(["-", "macd"])
class macd_IObservableFloatFloatFloat(object):
    """ 
    """ 
    def __init__(self, source = None, slow = None, fast = None):
        from marketsim.gen._out._const import const_Float as _const_Float
        from marketsim import deref_opt
        self.source = source if source is not None else deref_opt(_const_Float(1.0))
        self.slow = slow if slow is not None else 26.0
        self.fast = fast if fast is not None else 12.0
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'source' : IObservablefloat,
        'slow' : float,
        'fast' : float
    }
    
    
    
    
    
    
    def __repr__(self):
        return "MACD_{%(fast)s}^{%(slow)s}(%(source)s)" % dict([ (name, getattr(self, name)) for name in self._properties.iterkeys() ])
    
    def bind_ex(self, ctx):
        if self.__dict__.get('_bound_ex', False): return
        self.__dict__['_bound_ex'] = True
        if self.__dict__.get('_processing_ex', False):
            raise Exception('cycle detected')
        self.__dict__['_processing_ex'] = True
        self.__dict__['_ctx_ex'] = ctx.updatedFrom(self)
        self.source.bind_ex(self._ctx_ex)
        if hasattr(self, '_subscriptions'):
            for s in self._subscriptions: s.bind_ex(self.__dict__['_ctx_ex'])
        self.__dict__['_processing_ex'] = False
    
    def reset_ex(self, generation):
        if self.__dict__.get('_reset_generation_ex', -1) == generation: return
        self.__dict__['_reset_generation_ex'] = generation
        if self.__dict__.get('_processing_ex', False):
            raise Exception('cycle detected')
        self.__dict__['_processing_ex'] = True
        
        self.source.reset_ex(generation)
        if hasattr(self, '_subscriptions'):
            for s in self._subscriptions: s.reset_ex(generation)
        self.__dict__['_processing_ex'] = False
    
    def typecheck(self):
        from marketsim import rtti
        from marketsim.gen._out._iobservable._iobservablefloat import IObservablefloat
        rtti.typecheck(IObservablefloat, self.source)
        rtti.typecheck(float, self.slow)
        rtti.typecheck(float, self.fast)
    
    def registerIn(self, registry):
        if self.__dict__.get('_id', False): return
        self.__dict__['_id'] = True
        if self.__dict__.get('_processing_ex', False):
            raise Exception('cycle detected')
        self.__dict__['_processing_ex'] = True
        registry.insert(self)
        self.source.registerIn(registry)
        if hasattr(self, '_subscriptions'):
            for s in self._subscriptions: s.registerIn(registry)
        self.__dict__['_processing_ex'] = False
    

    def Histogram(self, timeframe = None,step = None):
        from marketsim.gen._out.math._histogram import Histogram
        return Histogram(self,timeframe,step)
    
    def Signal(self, timeframe = None,step = None):
        from marketsim.gen._out.math._signal import Signal
        return Signal(self,timeframe,step)
    
    @property
    def Fast(self):
        from marketsim.gen._out.math._fast import Fast
        return Fast(self)
    
    @property
    def Value(self):
        from marketsim.gen._out.math._value import Value
        return Value(self)
    
    @property
    def Slow(self):
        from marketsim.gen._out.math._slow import Slow
        return Slow(self)
    
    @property
    def Source(self):
        from marketsim.gen._out.math._source import Source
        return Source(self)
    
    pass
macd = macd_IObservableFloatFloatFloat
