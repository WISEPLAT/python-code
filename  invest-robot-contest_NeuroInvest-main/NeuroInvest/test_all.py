from trade_tuples import tradesTuple

import matplotlib.pyplot as plot


def showFigures(trades):
    for trade in trades:
        trade.update()
        dayData = trade.getMomentData()
        if dayData is not None:
            plot.figure()
            plot.grid(True)
            plot.title(trade.getName())
            plot.plot(dayData["tradeX"], dayData["tradeY"], linestyle='solid', marker='o', color='g')
            plot.plot(dayData["tradeX"], dayData["smoothY"], linestyle='dotted', color='b')

            if dayData["predictionsX"] is not None:
                plot.plot(dayData["predictionsX"], dayData["predictionsY"], linestyle='solid', color='r')


showFigures(tradesTuple)

plot.show()