import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, ticker, currency):
        self.ticker = ticker
        self.currency = currency
        self.fig = plt.figure()
        self.buys = []
        self.sells = []
        self.prices = {}

    def add_price(self, time, price: float):
        self.prices[time] = price

    def add_buy(self, time):
        self.buys.append(time)

    def add_sell(self, time):
        self.sells.append(time)

    def update_plot(self):
        self.fig.clear()

        x = list(self.prices.keys())[-50:]
        y = list(self.prices.values())[-50:]

        minx = min(x)
        buys = [buy for buy in self.buys if buy >= minx]
        sells = [sell for sell in self.sells if sell >= minx]

        plt.title(self.ticker)
        plt.xlabel('time')
        plt.ylabel(f'price ({self.currency})')
        plt.plot(x, y)
        plt.vlines(buys, ymin=min(y), ymax=max(y), color='g')
        plt.vlines(sells, ymin=min(y), ymax=max(y), color='r')
        plt.draw()
        plt.pause(0.2)
