package marketsim.orderbook

import marketsim._
import marketsim.MarketOrder
import marketsim.LimitOrder
import scala.Some

class Queue[T <: Entry](val tickSize : Double = 0.01) extends OrderQueue {

    private val orders = new ChunkDeque[T]()

    val BestPossiblyChanged = new Event[Option[PriceVolume]]
    val TradeDone = new Event[PriceVolume]

    import marketsim.Scheduler.async

    private def notifyBestChanged()
    {
        async {
            BestPossiblyChanged fire (if (orders.isEmpty) None else Some(orders.getTopPriceVolume))
        }
    }

    def insert(order : T) {
        orders insert order
        if (order.price == orders.top.price)
            notifyBestChanged()
    }

    def cancel(order : LimitOrder) =
        if (!orders.isEmpty) {
            val isTop = orders.top.order.price == order.price
            val e = orders cancel order
            if (e.nonEmpty)
                async { e.get.owner OnStopped (order, e.get.getVolumeUnmatchedSigned) }
            if (isTop)
                notifyBestChanged()
        }

    override def toString = orders.toString

    /**
     * Matches other market order against order queue
     * @return unmatched volume of the other order
     */
    def matchWith(other : MarketOrder, otherEvents : OrderListener) =
    {
        def inner(unmatched : Int) : Int =
        {
            if (orders.isEmpty || unmatched == 0)
                unmatched
            else {
                val mine = orders.top
                assert(other.side != mine.side)

                val trade_volume = mine matchWith (other, unmatched, otherEvents)

                async {
                    TradeDone fire (mine.order.price, trade_volume)
                }

                orders takeVolumeFromTop trade_volume

                if (mine.isEmpty) {
                    async { mine.owner OnStopped (mine.order, 0) }
                    orders.pop()
                    inner(unmatched - trade_volume)
                }
                else
                    0
            }
        }
        val ret = inner(other.volumeAbsolute)
        notifyBestChanged()
        ret
    }

    /**
     * Matches other market order against order queue
     * @return unmatched volume of the other order
     */
    def matchWith(other : LimitOrder, otherEvents : OrderListener) =
    {
        def inner(unmatched : Int) : Int =
        {
            if (orders.isEmpty || unmatched == 0)
                unmatched
            else {
                val mine = orders.top
                assert(other.side != mine.side)
                if (mine canMatchWith other)
                {
                    val trade_volume = mine matchWith (other, unmatched, otherEvents)

                    async {
                        TradeDone fire (mine.order.price, trade_volume)
                    }

                    orders takeVolumeFromTop trade_volume

                    if (mine.isEmpty) {
                        async { mine.owner OnStopped (mine.order, 0) }
                        orders.pop()
                        inner(unmatched - trade_volume)
                    }
                    else
                        0
                }
                else
                    unmatched
            }
        }
        val ret = inner(other.volumeAbsolute)
        notifyBestChanged()
        ret
    }
}
