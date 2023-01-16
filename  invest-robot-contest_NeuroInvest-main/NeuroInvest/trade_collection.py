from config import scanInterval, scanPeriod, trainingPeriod
from trade_moment import TradeMoment
from training import Training
from utility import currentTimestamp

from joblib import dump, load
from os import path

class TradeCollection:
    history = {}
    predictions = {}
    tradeName = ""
    maxScan = None
    minScan = None
    tradeMoment = TradeMoment()
    tradeFunction = None
    tradeModel = None


    def __init__(self, tradeName, getTradeFunction):
        self.tradeName = tradeName
        self.tradeFunction = getTradeFunction
        self.tradeModel = Training(self.__getModelFileName())
        self.__loadHistory()

        if len(self.history) > 0:
            self.minScan = min(self.history, key = int)
            self.maxScan = max(self.history, key = int)


    def update(self):
        self.__updateTradeData(updatePeriod = scanPeriod, onUpdateData = self.__onUpdateData)


    def __updateTradeData(self, updatePeriod, onUpdateData):
        end = currentTimestamp()

        if self.maxScan is None or self.maxScan + scanInterval - updatePeriod < self.minScan:
            start = end - updatePeriod
        else:
            start = int(self.maxScan) + 1

        if self.tradeFunction is not None and end - start > scanInterval and \
                ((self.maxScan is None or (end - self.maxScan) > scanInterval) or
                (self.minScan is None or start < self.minScan)) and \
                (self.minScan is None or self.maxScan is None or (updatePeriod / (int(self.maxScan) - int(self.minScan)) < 0.9)):
            self.tradeFunction(start, end, scanInterval, self.history, onUpdateData)
        else:
            onUpdateData()

    def __saveHistory(self):
        with open(self.__getDataFileName(), 'wb') as saveFile:
            dump(self.history, saveFile)


    def __loadHistory(self):
        if path.isfile(self.__getDataFileName()):
            with open(self.__getDataFileName(), 'rb') as loadFile:
                self.history = load(loadFile)

    # get coin pair history in last hours
    def getMomentData(self):
        return self.tradeMoment.getMomentData(self.history, self.tradeModel)


    def getName(self):
        return self.tradeName

    def __getDataFileName(self):
        return 'data/' + self.__getFileName() + ".trade"

    def __getModelFileName(self):
        return 'models/' + self.__getFileName()

    def __getFileName(self):
        return ''.join([self.tradeName.replace(character, "_") for character in "\\/?*" if character in self.tradeName]).replace(' ', '_')


    def training(self):
        self.__updateTradeData(updatePeriod = trainingPeriod, onUpdateData = self.__onUpdateTrainingData)

        if self.history is None:
            print("Cannot collect data for training")
            return False

        return True


    def __onUpdateTrainingData(self):
        self.__onUpdateData()

        if self.history is None:
            print("Cannot collect data for training")
            return False
        else:
            self.tradeModel.train(self.history)
            self.tradeModel.saveModel(self.__getModelFileName())
            return True


    def __onUpdateData(self):
        if self.history is None or len(self.history) == 0:
            self.minScan = None
            self.maxScan = None
        else:
            self.minScan = min(self.history, key = int)
            self.maxScan = max(self.history, key = int)

            self.history = dict(sorted(self.history.items()))
            self.__saveHistory()