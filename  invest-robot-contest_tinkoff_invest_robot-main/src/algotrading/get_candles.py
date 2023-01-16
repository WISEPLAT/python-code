import time
from datetime import timedelta

from tinkoff.invest import (
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
    CandleInterval,
)

from tinkoff.invest.utils import now

from src.algotrading import glossary


def get_all_candles(client, figi, periud_day, timeframe):
    candles = client.get_all_candles(
        figi=figi,
        from_=now() - timedelta(days=periud_day),
        interval=timeframe,
    )

    return candles


def request_iterator(figi, timeframe):
    print(timeframe)
    if timeframe == 1:
        interval = SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE
    else:
        interval = SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES

    yield MarketDataRequest(
        subscribe_candles_request=SubscribeCandlesRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
            instruments=[
                CandleInstrument(
                    figi=figi,
                    interval=interval,
                )
            ],
        )
    )
    while True:
        time.sleep(10)
