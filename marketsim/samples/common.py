import sys, itertools, pickle
sys.path.append(r'..')
sys.setrecursionlimit(10000)

from marketsim import (request, _, orderbook, observable, timeserie, scheduler, veusz, registry, event, config, 
                       context, trader, orderbook, Side, remote, ops, bind, signal, strategy, order)

simulations = {}

def expose(label, module, only_veusz=False):
    def inner(f):
        if module == '__main__':
            run(label, f, only_veusz)
        else:
            if not only_veusz:
                simulations[label] = f
        return f
    return inner
    
const = ops.constant 

def _print(*args):
    if len(args) == 1:
        print args[0],
    else:
        print args

class Context(object):
    
    def __init__(self, world, graph_renderer):
        
        self.world = world 
        self.book_A = orderbook.Local(tickSize=0.01, label="A")
        self.book_B = orderbook.Local(tickSize=0.01, label="B")
        self.book_C = orderbook.Local(tickSize=0.01, label="C")

        if config.showTiming:
            self.world.process(const(10), bind.Function(_print, '.'))
            self.world.process(const(100), bind.Function(_print, '\n'))
        
        delay = ops.constant(1.07)

        self.link_A = remote.TwoWayLink(remote.Link(delay), remote.Link(delay))
        self.link_B = remote.TwoWayLink(remote.Link(delay), remote.Link(delay))
        self.link_C = remote.TwoWayLink(remote.Link(delay), remote.Link(delay))

        self.remote_A = orderbook.Remote(self.book_A, self.link_A)
        self.remote_B = orderbook.Remote(self.book_B, self.link_B)
        self.remote_C = orderbook.Remote(self.book_C, self.link_C)

        self.graph = graph_renderer
        self.price_graph = self.graph("Price")
        self.askbid_graph = self.graph("AskBid")
        self.candles_graph = self.graph("Candles")
        self.avgs_graph = self.graph("Averages")
        self.macd_graph = self.graph("MACD")
        self.eff_graph = self.graph("efficiency")
        self.amount_graph = self.graph("amount")
        self.balance_graph = self.graph('balance')
        self.bollinger_a015_graph = self.graph('bollinger alpha 0.15')
        self.bollinger_20_graph = self.graph('bollinger 20')
        self.bollinger_100_graph = self.graph('bollinger 100')
        self.minmax_graph = self.graph('minmax')
        self.minors_eff_graph = self.graph('minor traders efficiency')
        self.minors_amount_graph = self.graph('minor traders position')
        
        self.graphs = [
                       self.price_graph, 
                       self.askbid_graph,
                       self.candles_graph,
                       self.avgs_graph,
                       self.macd_graph,
                       self.eff_graph, 
                       self.amount_graph,
                       self.balance_graph, 
                       self.bollinger_20_graph,
                       self.bollinger_a015_graph,
                       self.bollinger_100_graph,
                       self.minmax_graph, 
                       self.minors_eff_graph, 
                       self.minors_amount_graph
                       ]
         
        self.books = { 'Asset A' : self.book_A ,
                       'Asset B' : self.book_B , 
                       'Remote A': self.remote_A,
                       'Remote B': self.remote_B }
        
    def addGraph(self, name):
        graph = self.graph(name)
        self.graphs.append(graph)
        return graph
            
    def makeTrader(self, book, strategy, label, additional_ts = []):
        def trader_ts():
            thisTrader = trader.SingleProxy()
            return { 
                     observable.VolumeTraded(thisTrader) : self.amount_graph, 
                     #observable.PendingVolume(thisTrader): self.amount_graph, 
                     observable.Efficiency(thisTrader)   : self.eff_graph,
                     observable.PnL(thisTrader)          : self.balance_graph 
                   }
        
        t = trader.SingleAsset(book, strategy, label = label, timeseries = trader_ts())
                    
        for (ts, graph) in additional_ts:
            t.addTimeSerie(ts, graph)
            
        return t
    
    def makeMultiAssetTrader(self, books, aStrategy, label, additional_ts = []):
        traders = [self.makeTrader(b, strategy.Empty(), label + "_" + b.label) for b in books]
        t = trader.MultiAsset(traders, aStrategy, label = label)
                    
        for (ts, graph) in additional_ts:
            t.addTimeSerie(ts, graph)
            
        return t
    
    def makeMinorTrader(self, strategy, label):
        def trader_ts():
            thisTrader = trader.SingleProxy()
            return { observable.Efficiency(thisTrader)   : self.minors_eff_graph, 
                     observable.VolumeTraded(thisTrader) : self.minors_amount_graph    }
        
        return trader.SingleAsset(self.book_A, strategy, label = label, timeseries = trader_ts())
        
    def makeTrader_A(self, strategy, label, additional_ts = []):
        return self.makeTrader(self.book_A, strategy, label, additional_ts)
    
    def makeTrader_rA(self, strategy, label, additional_ts = []):
        return self.makeTrader(self.remote_A, strategy, label, additional_ts)
    
    def makeTrader_B(self, strategy, label, additional_ts = []):
        return self.makeTrader(self.book_B, strategy, label, additional_ts)

    def makeTrader_C(self, strategy, label, additional_ts = []):
        return self.makeTrader(self.book_C, strategy, label, additional_ts)

def orderBooksToRender(ctx, traders):
        books = list(set(itertools.chain(*[t.orderBooks for t in traders]))) 
        
        books = filter(lambda b: type(b) is orderbook.Local, books)       
        
        graphs = ctx.graphs
        
        def orderbook_ts():
            from marketsim.gen._out.observable._Max import Max

            thisBook = orderbook.Proxy()
            assetPrice = observable.MidPrice(thisBook)
            askPrice = observable.AskPrice(thisBook)
            bidPrice = observable.BidPrice(thisBook)
            askWeightedPrice = observable.AskWeightedPrice(thisBook, 0.15)
            bidWeightedPrice = observable.BidWeightedPrice(thisBook, 0.15)
            avg = observable.avg
            cma = observable.CMA(assetPrice)
            stddev = observable.StdDev(assetPrice)
            ma100 = observable.MA(assetPrice, 100)
            ma20 = observable.MA(assetPrice, 20)
            stddev100 = observable.StdDevRolling(assetPrice, 100)
            stddev20 = observable.StdDevRolling(assetPrice, 20)
            ewma015 = observable.EWMA(assetPrice, alpha=0.15)
            ewmsd = observable.StdDevEW(assetPrice, 0.15)
            min = observable.Min(assetPrice, 100)
            max = observable.Max(assetPrice, 100)
            candlesticks = observable.CandleSticks(assetPrice, 10)
            tickSize = observable.TickSize(thisBook)
            max_eps = observable.MaxEpsilon(assetPrice, tickSize)
            min_eps = observable.MinEpsilon(assetPrice, tickSize)
            
            def bollinger(mean, stddev, graph):
                return [
                    timeserie.ToRecord(assetPrice, graph), 
                    timeserie.ToRecord(observable.OnEveryDt(1, mean), graph), 
                    timeserie.ToRecord(observable.OnEveryDt(1, mean + stddev*2), graph), 
                    timeserie.ToRecord(observable.OnEveryDt(1, mean - stddev*2), graph),
                ] 
                
            scaled = (assetPrice - 100) / 10
            
            return ([
                timeserie.ToRecord(assetPrice, ctx.price_graph), 
                timeserie.ToRecord(askPrice, ctx.price_graph),
                timeserie.ToRecord(bidPrice, ctx.price_graph),
                #timeserie.ToRecord(observable.Spread(thisBook), ctx.price_graph),

                timeserie.ToRecord(observable.AskLastTradePrice(thisBook), ctx.askbid_graph),
                timeserie.ToRecord(observable.BidLastTradePrice(thisBook), ctx.askbid_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, askWeightedPrice), ctx.askbid_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, bidWeightedPrice), ctx.askbid_graph), 
                
                #timeserie.ToRecord(assetPrice, ctx.candles_graph), 
                timeserie.ToRecord(candlesticks, ctx.candles_graph),

                timeserie.ToRecord(assetPrice, ctx.avgs_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, cma), ctx.avgs_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, ma20), ctx.avgs_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, ma100), ctx.avgs_graph), 
                timeserie.ToRecord(avg(assetPrice, alpha=0.15), ctx.avgs_graph),
                timeserie.ToRecord(avg(assetPrice, alpha=0.65), ctx.avgs_graph),
                timeserie.ToRecord(avg(assetPrice, alpha=0.015), ctx.avgs_graph),
                 
                timeserie.ToRecord(scaled, ctx.macd_graph), 
                timeserie.ToRecord(avg(scaled, alpha=2./13), ctx.macd_graph),
                timeserie.ToRecord(avg(scaled, alpha=2./27), ctx.macd_graph),
                timeserie.ToRecord(observable.OnEveryDt(1, observable.MACD(assetPrice)), ctx.macd_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, observable.MACD_signal(assetPrice)), ctx.macd_graph), 
                timeserie.ToRecord(observable.OnEveryDt(1, observable.MACD_histogram(assetPrice)), ctx.macd_graph), 

                timeserie.ToRecord(assetPrice, ctx.minmax_graph),
                timeserie.ToRecord(max, ctx.minmax_graph),
                timeserie.ToRecord(min, ctx.minmax_graph),
                timeserie.ToRecord(max_eps, ctx.minmax_graph),
                timeserie.ToRecord(min_eps, ctx.minmax_graph),
            ] 
            + bollinger(ma100, stddev100, ctx.bollinger_100_graph) 
            + bollinger(ma20, stddev20, ctx.bollinger_20_graph)
            + bollinger(ewma015, ewmsd, ctx.bollinger_a015_graph)
            )

        for b in books:
            b.volumes_graph = ctx.addGraph("Volume levels " + b.label)
            thisBook = orderbook.Proxy()
            ts = orderbook_ts()
            ts.append(timeserie.VolumeLevels(
                           observable.VolumeLevels(1, 
                                                   thisBook, 
                                                   Side.Sell, 
                                                   30, 
                                                   10), 
                           b.volumes_graph))
            ts.append(timeserie.VolumeLevels(
                           observable.VolumeLevels(1, 
                                                   thisBook, 
                                                   Side.Buy, 
                                                   30, 
                                                   10), 
                           b.volumes_graph))
            b.timeseries = ts
             
            b.rsi_graph = ctx.addGraph("RSI " + b.label)
            ts.append(timeserie.ToRecord(observable.MidPrice(thisBook), b.rsi_graph))
            for timeframe in [#0., 
                              #0.001,
                              #0.01,
                              0.1, 
                              #0.3, 
                              0.5, 
                              1., 
                              #1.5, 
                              2, 
                              #3, 
                              #4, 
                              5]:
                ts.append(
                    timeserie.ToRecord(
                        observable.OnEveryDt(1, 
                            observable.RSI(thisBook, 
                                           timeframe, 
                                           1./14)), 
                        b.rsi_graph))
            
        return books
    
runTwoTimes = True

def run(name, constructor, only_veusz):
    with scheduler.create() as world:
        
        ctx = Context(world, veusz.Graph)
        traders = constructor(ctx)

        if config.useMinorTraders:
            traders.extend([
                ctx.makeMinorTrader(strategy.RSI_linear(k = const(0.07)), "RSI 0.07"),
                ctx.makeMinorTrader(strategy.RSI_linear(k = const(-0.07)), "RSI -0.07"),
                ctx.makeMinorTrader(strategy.Bollinger_linear(alpha=0.15, k = const(-0.5)), "Bollinger -0.5"),
                ctx.makeMinorTrader(strategy.Bollinger_linear(alpha=0.15, k = const(+0.5)), "Bollinger +0.5"),
            ])
        
        books = orderBooksToRender(ctx, traders)
        
        for t in traders + books:
            for ts in t.timeseries:
                ts.graph.addTimeSerie(ts)
        
        r = registry.create()
        root = registry.Simulation(traders, list(ctx.books.itervalues()), ctx.graphs)
        r.insert(root)
        r.pushAllReferences()
        context.bind(root, {'world' : world })
                    
        if False:
            req = request.EvalMarketOrder(Side.Sell, 500, _print)
            world.schedule(10, _(ctx.remote_A, req).process)
        
        def checks():
            if not only_veusz and config.checkConsistency:
                r.typecheck()
                try:
                    dumped = pickle.dumps(r)
                    pickle.loads(dumped)
                except Exception, err:
                    print err

        checks()        
        stat = world.workTill(500)
        checks()        

        if config.showTiming:
            print "\n", stat
        
        non_empty_graphs = [g for g in ctx.graphs if len(g._datas)]
        
        veusz.render(name, non_empty_graphs)
        
        world._reset()
        context.reset(root)

        if False and config.runTwoTimes:
            world.workTill(500)
            veusz.render(name, non_empty_graphs)

def Constant(c, demo):
    return [(observable.OnEveryDt(10, ops.constant(c)), demo)]

class Interlacing(ops.Function[float]):

    def __init__(self, phase = 1, timeframe = 10):
        self.timeframe = timeframe
        self.phase = phase
    
    def bind(self, ctx):
        self._scheduler = ctx.world
        
    def __call__(self):
        return int(self._scheduler.currentTime / self.timeframe) % 2 * 2 - 1

class InterlacingSide(ops.Function[Side]):
    
    def __init__(self, phase = 1, timeframe = 10):
        self._impl = Interlacing(phase, timeframe)
        
    _internals = ['_impl']
        
    def __call__(self):
        return Side.Buy if self._impl() > 0 else Side.Sell 
