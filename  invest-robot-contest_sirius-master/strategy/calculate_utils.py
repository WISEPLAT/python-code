from utils.util import price_to_float


def calculate_ma(candles, period, argument_name, ma_name):
    current_period = 0
    avg_val = 0

    for i in range(1, len(candles) + 1):
        candle = candles[-i]
        avg_val = avg_val + candle[argument_name]
        current_period = current_period + 1

        if current_period >= period or i == len(candles):
            avg_val = avg_val / current_period
            for j in range(0, current_period):
                candles[-i + j][ma_name] = avg_val

            current_period = 0
            avg_val = 0


def add_prices_to_candles(candles):
    close_prices = []

    for candle in candles:
        close_price = price_to_float(candle['close']['units'], candle['close']['nano'])
        candle_time = candle['time']
        close_prices.append({'time': candle_time, 'candle': candle, 'price': close_price})
    return close_prices


def calc_profit_percent(price, buy_price):
    percent = price / buy_price * 100 - 100
    return percent
