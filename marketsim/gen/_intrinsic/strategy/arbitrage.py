from marketsim import Side, event, _

from marketsim.gen._out.order._ImmediateOrCancel import ImmediateOrCancel
from marketsim.gen._out.order._Limit import Limit

from basic import MultiAssetStrategy

class _Arbitrage_Impl(MultiAssetStrategy):

    def __init__(self):
        """ Initializes trader by order books for the asset from different markets
        """
        MultiAssetStrategy.__init__(self)
        from blist import sorteddict

        # order queues ordered by their best asks and bids
        # something like std::map<Ticks, OrderQueue>[2]
        self._bests = [sorteddict(), sorteddict()]
        self._oldBests = {}
        
    def inner(self, myQueue, side):
        """Called when in some queue a new best order appeared"""
        
        # ordered set of queues on my side
        myQueues = self._bests[side.id]
        oppositeSide = side.opposite
        # ordered set of queues on the opposite side
        oppositeQueues = self._bests[oppositeSide.id]

        bestOrder = myQueue.best if not myQueue.empty else None
        
        # since the price of the best order changed,
        # we remove its queue from the set of all queues
        if myQueue in self._oldBests:
            try:
                p = self._oldBests[myQueue]
                myQueues.pop(p)
            except Exception:    
                pass # very strange things...
        
        # if the queue becomes empty 
        if bestOrder == None:
            # just remove it from the set of all queues
            if myQueue in self._oldBests:
                self._oldBests.pop(myQueue)
        else:
            # otherwise, update correspondance queue -> signedPrice -> queue
            self._oldBests[myQueue] = bestOrder.signedPrice
            myQueues[bestOrder.signedPrice] = myQueue
        
            # if there are opposite queues    
            if len(oppositeQueues) > 0:
                # take the best price of the best one
                bestOppositeSignedPrice = oppositeQueues.viewkeys()[0]
                # and the queue itself
                oppositeQueue = oppositeQueues[bestOppositeSignedPrice] 

                if oppositeQueue.empty or oppositeQueue.best.price != abs(bestOppositeSignedPrice):
                    # it means that we haven't yet received event that another queue has changed 
                    return 
                
                oppositePrice = abs(bestOppositeSignedPrice)
                myPrice = bestOrder.price
                
                # is there some sense to trade                    
                if not side.better(oppositePrice, myPrice):
                    
                    volumeToTrade = min(bestOrder.volumeUnmatched, oppositeQueue.best.volumeUnmatched)

                    # make two complimentary trades
                    # for these trades we create limit orders 
                    # since price may change before orders will be processed
                    # but cancel them immediately in order to avoid storing these limit orders in the book
                    # this logic is implemented by ImmediateOrCancelOrder
                    
                    def send(o):
                        self._send(myQueue.book, o)

                    from marketsim.ops._all import constant
                        
                    send(ImmediateOrCancel(
                                        Limit(
                                                 constant(oppositeSide),
                                                 constant(myPrice),
                                                 constant(volumeToTrade)))())
                    
                    
                    send(ImmediateOrCancel(
                                        Limit(
                                                 constant(side),
                                                 constant(oppositePrice),
                                                 constant(volumeToTrade)))())
                    
    def _send(self, orderbook, order):
        if order is not None:
            for t in self._traders:
                if t.orderBook == orderbook:
                    t.send(order)
                    
    def _schedule(self, side, queue):
        self.inner(queue, side)
    
    def bind(self, context):
        self._traders = [t for t in self._trader.traders]
        self._books = [t.orderBook for t in self._trader.traders]        
                        
        def regSide(side):
            for book in self._books:
                queue = book.queue(side) 
                event.subscribe(queue.bestPrice, 
                                _(self, side)._schedule, 
                                self, {})
                if not queue.empty:
                    self._bests[side.id][queue.best.signedPrice] = queue
                    self._oldBests[queue] = queue.best.signedPrice
                    
        regSide(Side.Buy)
        regSide(Side.Sell)
