from trade_tuples import tradesTuple

def trainingsAll(trades):
    for trade in trades:
        trade.training()


trainingsAll(tradesTuple)