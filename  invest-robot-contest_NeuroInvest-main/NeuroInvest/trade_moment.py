from config import scanInterval, scanPeriod
from kalman import Kalman
from utility import currentTimestamp

class TradeMoment:
    __lastMomentStart = None
    __kalman = None
    __tradeX = None
    __tradeY = None
    __predictionsX = None
    __predictionsY = None

    def getMomentData(self, history, tradeModel):
        now = currentTimestamp()
        momentStart = now - scanPeriod

        if self.__lastMomentStart is None or self.__lastMomentStart < momentStart - scanInterval:
            dayHistory = {valueTime: value for valueTime, value in history.items() if valueTime >= momentStart}

            if dayHistory is not None and len(dayHistory) > 0:
                self.__kalman = Kalman(dayHistory)
                self.__tradeX, self.__tradeY = zip(*dayHistory.items())

                if tradeModel is not None:
                    self.__updatePredictions(tradeModel, now)

                return {"tradeX": self.__tradeX, "tradeY": self.__tradeY, "smoothY": list(self.__kalman.getSmoothData()),
                        "predictionsX": self.__predictionsX, "predictionsY": self.__predictionsY}

        return None


    def __updatePredictions(self, tradeModel, nowTime):
        predictions = tradeModel.tradePredict(list(self.__tradeY), nowTime)

        if predictions is not None:
            self.__predictionsX, self.__predictionsY = zip(*predictions.items())

            self.__predictionsX = self.__tradeX[len(self.__tradeX) - 1:] + self.__predictionsX
            self.__predictionsY = self.__tradeY[len(self.__tradeY) - 1:] + self.__predictionsY