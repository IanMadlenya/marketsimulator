from marketsim import parts, _, defs, ops, order, orderbook, observable, registry, types
from marketsim.types import *

from .. import _wrap
from .._generic import Generic

class Bollinger_linear(types.ISingleAssetStrategy):

    def getImpl(self):
        return Generic(
                    self.orderFactory(
                        parts.signed_volume.Bollinger_linear(self.alpha, self.k)))
        
_wrap.strategy(Bollinger_linear, ['Desired position', 'Bollinger linear'], 
               """
               """, 
               [
                  ('orderFactory', 'order.factory.signedvolume.Market()', 'IFunction[float] -> IOrderGenerator'),
                  ('alpha',        '0.15',                'non_negative'), 
                  ('k',            'ops.constant(+0.5)',  'IFunction[float]'), 
               ], globals())

