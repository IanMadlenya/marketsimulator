from marketsim.veusz_graph import Graph, showGraphs
import random
from marketsim.indicator import AssetPrice, OnEveryDt, EWMA, TraderEfficiency, PnL

from marketsim import strategy, orderbook, trader, scheduler

world = scheduler.create()

book_A = orderbook.Local(tickSize=0.01, label="A")
book_B = orderbook.Local(tickSize=0.01, label="B")

price_graph = Graph("Price")
 
assetPrice_A = AssetPrice(book_A)
price_graph.addTimeSerie(assetPrice_A)

assetPrice_B = AssetPrice(book_B)
price_graph.addTimeSerie(assetPrice_B)

def avg(source, alpha=0.15):
    return OnEveryDt(1, EWMA(source, alpha))

ewma_0_15 = EWMA(assetPrice_A, alpha=0.15)
ewma_0_015 = EWMA(assetPrice_A, alpha=0.015)
ewma_0_065 = EWMA(assetPrice_A, alpha=0.065)

price_graph.addTimeSerie(avg(assetPrice_A, alpha=0.15))
price_graph.addTimeSerie(avg(assetPrice_A, alpha=0.015), {r'PlotLine/bezierJoin':True})
price_graph.addTimeSerie(avg(assetPrice_A, alpha=0.65))

price_graph.addTimeSerie(avg(assetPrice_B, alpha=0.15))
price_graph.addTimeSerie(avg(assetPrice_B, alpha=0.015), {r'PlotLine/bezierJoin':True})
price_graph.addTimeSerie(avg(assetPrice_B, alpha=0.65))

liqVol = lambda: random.expovariate(.1)*5
lp_A = strategy.LiquidityProvider(trader.SASM(book_A), defaultValue=50., volumeDistr=liqVol).trader
lp_B = strategy.LiquidityProvider(trader.SASM(book_B), defaultValue=150., volumeDistr=liqVol).trader

dep_AB = strategy.Dependency(trader.SASM(book_A, "AB"), book_B, factor=2).trader
dep_BA = strategy.Dependency(trader.SASM(book_B, "BA"), book_A, factor=.5).trader

dep_AB.efficiency = TraderEfficiency([dep_AB.on_traded], dep_AB)
dep_BA.efficiency = TraderEfficiency([dep_BA.on_traded], dep_BA)

eff_graph = Graph("efficiency")
eff_graph.addTimeSerie(dep_AB.efficiency)
eff_graph.addTimeSerie(dep_BA.efficiency)
eff_graph.addTimeSerie(PnL(dep_AB))
eff_graph.addTimeSerie(PnL(dep_BA))

world.workTill(500)

showGraphs("dependency", [price_graph, eff_graph])
