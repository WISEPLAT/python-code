from loguru import logger

from ta.trend import macd, macd_signal
from pandas import DataFrame
import numpy as np

from src.algotrading._sandbox_accounts import post_sandbox_order
from src.algotrading.get_candles import get_all_candles, request_iterator
from src.algotrading.instruments_service import get_instrument_by
from src.algotrading.utils import api_client_configure, to_float


def create_df(candles):
    df = DataFrame([{
        'time': c.time,
        'volume': c.volume,
        'open': to_float(c.open),
        'close': to_float(c.close),
        'high': to_float(c.high),
        'low': to_float(c.low),
    } for c in candles])

    return df


def macd_test(data: dict) -> int:
    instrument_data = get_instrument_by(data['figi'])
    api_client = api_client_configure()

    with api_client as client:

        candles = get_all_candles(client, data['figi'], 7, data['timeframe'])
        df = create_df(candles)

        df['macd'] = macd(close=df['close'], window_slow=data['window_slow'], window_fast=data['window_fast'])
        df['macd_signal'] = macd_signal(close=df['close'],
                                        window_slow=data['window_slow'],
                                        window_fast=data['window_fast'],
                                        window_sign=data['window_sign']
                                        )

        df['trading_signal'] = np.where(df['macd'] > df['macd_signal'], 1, 0)

        result = 0
        count_operation = 0
        for index, row in df.iterrows():
            if index == 1:
                continue
            elif row['trading_signal'] > df.iloc[index - 1]['trading_signal']:
                logger.info(f"Покупаем {row.time} по {row['close']}")
                result -= row['close'] * instrument_data['lot']
                count_operation += 1
            elif row['trading_signal'] < df.iloc[index - 1]['trading_signal']:
                logger.info(f"Продажа {row.time} по {row['close']}")
                result += row['close'] * instrument_data['lot']
                count_operation += 1

    return {'result': result, 'count_operation': count_operation, 'currency': instrument_data['currency']}


def macd_sandbox_run(data: dict):
    instrument_data = get_instrument_by(data['figi'])
    api_client = api_client_configure()
    candles = {}
    positions = False

    with api_client as client:
        for marketdata in client.market_data_stream.market_data_stream(
                request_iterator(data['figi'], data['timeframe'])
        ):

            if marketdata.candle:
                candles[int(marketdata.candle.time.timestamp())] = marketdata.candle

                df = create_df(candles.values())

                df['macd'] = macd(close=df['close'], window_slow=data['window_slow'], window_fast=data['window_fast'])
                df['macd_signal'] = macd_signal(close=df['close'],
                                                window_slow=data['window_slow'],
                                                window_fast=data['window_fast'],
                                                window_sign=data['window_sign']
                                                )
                df['trading_signal'] = np.where(df['macd'] > df['macd_signal'], 1, 0)


                if df.iloc[-1]['trading_signal'] and not positions:
                    logger.info(f"Покупаем {marketdata.candle.time} по {to_float(marketdata.candle.close)}")
                    post_sandbox_order(client, data['account_id'], data['figi'], 'buy')
                    positions = True

                elif not df.iloc[-1]['trading_signal'] and positions:
                    logger.info(f"Продаем {marketdata.candle.time} по {to_float(marketdata.candle.close)}")
                    positions = False
                    post_sandbox_order(client, data['account_id'], data['figi'], 'sell')

                else:
                    logger.trace(f"\n{df.tail(5)}")

            logger.trace(f"\n{marketdata}")


if __name__ == "__main__":
    data = {'account_id': 'f10a6f40-711b-4a0a-855c-6bf43b7eba77', 'figi': 'BBG004730N88', 'window_slow': 26,
            'window_fast': 12, 'window_sign': 9}
    macd_sandbox_run(data)
