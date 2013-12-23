from marketsim import registry
from marketsim import float
from marketsim.ops._all import Observable
from marketsim import IOrderBook
from marketsim import context
@registry.expose(["Basic", "RSI"])
class RSI(Observable[float]):
    """ 
    """ 
    def __init__(self, book = None, timeframe = None, alpha = None):
        from marketsim import float
        from marketsim.ops._all import Observable
        from marketsim.gen._out.observable.orderbook._OfTrader import OfTrader
        from marketsim import _
        from marketsim import event
        Observable[float].__init__(self)
        self.book = book if book is not None else OfTrader()
        self.timeframe = timeframe if timeframe is not None else 10.0
        self.alpha = alpha if alpha is not None else 0.015
        self.impl = self.getImpl()
        event.subscribe(self.impl, _(self).fire, self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'book' : IOrderBook,
        'timeframe' : float,
        'alpha' : float
    }
    def __repr__(self):
        return "RSI_{%(timeframe)s}^{%(alpha)s}(%(book)s)" % self.__dict__
    
    _internals = ['impl']
    def getImpl(self):
        from marketsim.gen._out._const import const
        from marketsim.gen._out._const import const
        from marketsim.gen._out._const import const
        from marketsim.gen._out.observable.rsi._Raw import Raw
        from marketsim.gen._out.observable.orderbook._MidPrice import MidPrice
        return const(100.0)-const(100.0)/(const(1.0)+Raw(MidPrice(self.book),self.timeframe,self.alpha))
        
        
        
        
    
    def bind(self, ctx):
        self._ctx = ctx.clone()
    
    def reset(self):
        self.impl = self.getImpl()
        ctx = getattr(self, '_ctx', None)
        if ctx: context.bind(self.impl, ctx)
    
    def __call__(self, *args, **kwargs):
        return self.impl()
    
