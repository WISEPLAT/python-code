from tinkoff_api import Tinkoff
from south_x_change import SouthXChange
from config import TinkoffTrade

# tuple of trade pairs
tradesTuple = (Tinkoff(TinkoffTrade.APPLE), Tinkoff(TinkoffTrade.GAZPROM_OIL), SouthXChange("DOGE/BTC"))