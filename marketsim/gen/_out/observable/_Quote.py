# generated with class generator.python.intrinsic_observable$Import
from marketsim import registry
from marketsim.gen._out._observable._observablefloat import Observablefloat
from marketsim.gen._intrinsic.observable.quote import Quote_Impl
@registry.expose(["Basic", "Quote"])
class Quote_StringStringString(Observablefloat,Quote_Impl):
    """ **Observable that downloads closing prices for every day from *start* to *end* for asset given by *ticker***
    
      and follows the price in scale 1 model unit of time = 1 real day
    
    Parameters are:
    
    **ticker**
    	 defines quotes to download 
    
    **start**
    	 defines first day to download in form YYYY-MM-DD 
    
    **end**
    	 defines last day to download in form YYYY-MM-DD 
    """ 
    def __init__(self, ticker = None, start = None, end = None):
        from marketsim.gen._out._observable._observablefloat import Observablefloat
        Observablefloat.__init__(self)
        self.ticker = ticker if ticker is not None else "^GSPC"
        self.start = start if start is not None else "2001-1-1"
        self.end = end if end is not None else "2010-1-1"
        Quote_Impl.__init__(self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'ticker' : str,
        'start' : str,
        'end' : str
    }
    
    
    
    
    
    
    
    
    
    def __repr__(self):
        return "%(ticker)s" % dict([ (name, getattr(self, name)) for name in self._properties.iterkeys() ])
    
    def bind_ex(self, ctx):
        if self.__dict__.get('_bound_ex', False): return
        self.__dict__['_bound_ex'] = True
        if self.__dict__.get('_processing_ex', False):
            raise Exception('cycle detected')
        self.__dict__['_processing_ex'] = True
        self.__dict__['_ctx_ex'] = ctx.updatedFrom(self)
        if hasattr(self, '_internals'):
            for t in self._internals:
                v = getattr(self, t)
                if type(v) in [list, set]:
                    for w in v: w.bind_ex(self.__dict__['_ctx_ex'])
                else:
                    v.bind_ex(self.__dict__['_ctx_ex'])
        
        self.bind_impl(self.__dict__['_ctx_ex'])
        if hasattr(self, '_subscriptions'):
            for s in self._subscriptions: s.bind_ex(self.__dict__['_ctx_ex'])
        self.__dict__['_processing_ex'] = False
    
    def reset_ex(self, generation):
        if self.__dict__.get('_reset_generation_ex', -1) == generation: return
        self.__dict__['_reset_generation_ex'] = generation
        if self.__dict__.get('_processing_ex', False):
            raise Exception('cycle detected')
        self.__dict__['_processing_ex'] = True
        if hasattr(self, '_internals'):
            for t in self._internals:
                v = getattr(self, t)
                if type(v) in [list, set]:
                    for w in v: w.reset_ex(generation)
                else:
                    v.reset_ex(generation)
        
        self.reset()
        if hasattr(self, '_subscriptions'):
            for s in self._subscriptions: s.reset_ex(generation)
        self.__dict__['_processing_ex'] = False
    
    def typecheck(self):
        from marketsim import rtti
        rtti.typecheck(str, self.ticker)
        rtti.typecheck(str, self.start)
        rtti.typecheck(str, self.end)
    
    def registerIn(self, registry):
        if self.__dict__.get('_id', False): return
        self.__dict__['_id'] = True
        if self.__dict__.get('_processing_ex', False):
            raise Exception('cycle detected')
        self.__dict__['_processing_ex'] = True
        registry.insert(self)
        
        if hasattr(self, '_subscriptions'):
            for s in self._subscriptions: s.registerIn(registry)
        if hasattr(self, '_internals'):
            for t in self._internals:
                v = getattr(self, t)
                if type(v) in [list, set]:
                    for w in v: w.registerIn(registry)
                else:
                    v.registerIn(registry)
        self.__dict__['_processing_ex'] = False
    
    def bind_impl(self, ctx):
        Quote_Impl.bind_impl(self, ctx)
    
    def reset(self):
        Quote_Impl.reset(self)
    
def Quote(ticker = None,start = None,end = None): 
    from marketsim import rtti
    if ticker is None or rtti.can_be_casted(ticker, str):
        if start is None or rtti.can_be_casted(start, str):
            if end is None or rtti.can_be_casted(end, str):
                return Quote_StringStringString(ticker,start,end)
    raise Exception('Cannot find suitable overload for Quote('+str(ticker) +':'+ str(type(ticker))+','+str(start) +':'+ str(type(start))+','+str(end) +':'+ str(type(end))+')')
