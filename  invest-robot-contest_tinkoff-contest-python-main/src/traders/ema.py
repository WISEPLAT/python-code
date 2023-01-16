from typing import List

from src.containers.market import TraderDecision, MarketState
from src.traders.base import BaseTrader


class EMATrader(BaseTrader):
    _trader_name = "ema"

    async def make_decisions(self, state: MarketState) -> List[TraderDecision]:
        return []
