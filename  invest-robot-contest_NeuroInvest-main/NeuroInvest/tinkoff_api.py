from config import tinkoffAPIToken, scanInterval, tinkoffScanInterval

from tinkoff.investments import Environment, TinkoffInvestmentsRESTClient
from tinkoff.investments.client.exceptions import TinkoffInvestmentsUnavailableError, TinkoffInvestmentsConnectionError, \
    TinkoffInvestmentsUnauthorizedError
from tinkoff.investments.utils.historical_data import HistoricalData

from asyncio import get_event_loop
from datetime import datetime
from trade_collection import TradeCollection

class Tinkoff(TradeCollection):
    __figi = None
    __completeFunction = None

    def __init__(self, tinkoffTrade):
        self.__figi = tinkoffTrade.value[0]["figi"]
        super().__init__(tinkoffTrade.value[0]["name"], self.getData)

    # noinspection PyUnusedLocal
    def getData(self, start, end, stepInSeconds, history, onUpdateData):
        self.__completeFunction = onUpdateData

        startTime = datetime.utcfromtimestamp(int(start / scanInterval) * scanInterval)
        endTime = datetime.utcfromtimestamp(int(end / scanInterval) * scanInterval)

        loop = get_event_loop()

        async def onComplete():
            onUpdateData()

        async def prepareCandles(candle):
            time = candle.time.timestamp()
            value = (candle.h + candle.l) / 2.0
            history[time] = value
            print(time, candle.time, value)

        async def getCandles():
            try:
                async with TinkoffInvestmentsRESTClient(
                        token = tinkoffAPIToken,
                        environment = Environment.SANDBOX) as client:
                    historical_data = HistoricalData(client)

                    async for candle in historical_data.iter_candles(
                            figi = self.__figi,
                            dt_from = startTime,
                            dt_to = endTime,
                            interval = tinkoffScanInterval):
                        await prepareCandles(candle)

            except TinkoffInvestmentsUnauthorizedError:
                print("Invalid token. Please check it in config.py!")
                loop.stop()
                await onComplete()

            except TinkoffInvestmentsConnectionError as message:
                print("Connect error: " + str(message))
                loop.stop()
                await onComplete()

            except TinkoffInvestmentsUnavailableError as message:
                print("Unavailable data: " + str(message))
                loop.stop()
                await onComplete()

            except Exception as message:
                print("Unexpected error: " + str(message))
                loop.stop()
                await onComplete()


        loop.run_until_complete(getCandles())
        loop.run_until_complete(onComplete())
        return True
