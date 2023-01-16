from config import scanInterval

from json import loads
from requests import get
from datetime import datetime
from trade_collection import TradeCollection
from time import sleep

class SouthXChange(TradeCollection):
    def __init__(self, coinName):
        super().__init__(coinName, self.getData)

    maxScanPeriod = 500 * scanInterval

    def getData(self, start, end, stepInSeconds, history, onUpdateData):
        for scanStart in range(start, end, self.maxScanPeriod):
            if not self.__getLimitedData(super().getName(), scanStart, min(scanStart + self.maxScanPeriod, end), stepInSeconds, history):
                return False

        if onUpdateData is not None:
            onUpdateData()

        return True

    @staticmethod
    def __getLimitedData(name, start, end, stepInSeconds, history):
        try:
            steps = int((end - start) / stepInSeconds)
            url = "https://www.southxchange.com/api/history/" + name + "/" + str(start * 1000) + "/" + str(end * 1000) + "/" + str(steps)

            response = get(url=url)
            result = loads(response.text)

            print("SouthXChange FROM " + str(start) + " TO " + str(end))

            sleep(1)

            for data in result:
                valueTime = int(datetime.fromisoformat(data["Date"] + "+00:00").timestamp())
                history[valueTime] = (data["PriceHigh"] + data["PriceLow"]) / 2

            return True
        except Exception as message:
            print("SouthXChange ERROR: " + str(message))
            return False
