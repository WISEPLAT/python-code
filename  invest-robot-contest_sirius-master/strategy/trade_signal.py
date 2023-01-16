from strategy.calculate_utils import calculate_ma
from utils.settings import settings

fast_ma_step = int(settings()['TRADE']['fast_ma_step'])
slow_ma_step = int(settings()['TRADE']['slow_ma_step'])
trend_ma_step = int(settings()['TRADE']['trend_ma_step'])


def break_from_down(candles, name_first, name_second):
    return candles[0][name_first] < candles[0][name_second] and \
           candles[-1][name_first] > candles[-1][name_second]


def break_from_up(candles, name_first, name_second):
    return candles[0][name_first] > candles[0][name_second] and \
           candles[-1][name_first] < candles[-1][name_second]


def get_trade_signal(candles):
    min_time_frame_minutes = 30
    signal = ''

    if len(candles) < min_time_frame_minutes:
        return signal

    calculate_ma(candles, fast_ma_step, 'price', 'fast_ma')
    calculate_ma(candles, slow_ma_step, 'price', 'slow_ma')
    calculate_ma(candles, trend_ma_step, 'price', 'trend_ma')

    if break_from_down(candles, 'fast_ma', 'slow_ma') and break_from_down(candles, 'fast_ma', 'trend_ma'):
        signal = 'buy'
    if break_from_up(candles, 'fast_ma', 'slow_ma') and break_from_up(candles, 'fast_ma', 'trend_ma'):
        signal = 'sell'

    return signal


