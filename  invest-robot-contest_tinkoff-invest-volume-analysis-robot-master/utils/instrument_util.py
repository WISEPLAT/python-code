import asyncio
from datetime import datetime

from tinkoff.invest import TradeInstrument, MarketDataRequest, SubscribeTradesRequest, SubscriptionAction

from settings import INSTRUMENTS


async def request_iterator(instruments):
    figi_instruments = list(map(lambda instrument: TradeInstrument(instrument["figi"]), instruments))
    yield MarketDataRequest(
        subscribe_trades_request=SubscribeTradesRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
            instruments=figi_instruments,
        )
    )
    while True:
        await asyncio.sleep(1)


def get_file_path_by_instrument(instrument):
    return f"./data/{instrument['name']}-{datetime.now().strftime('%Y%m%d')}.csv"


def get_instrument_by_name(name: str):
    return next(item for item in INSTRUMENTS if item["name"] == name)
