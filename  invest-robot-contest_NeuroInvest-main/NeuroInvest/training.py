from config import predictPeriod, scanInterval, predictionIntervals
from kalman import Kalman

from pandas import DataFrame
from sklearn import neural_network
from sklearn.preprocessing import MinMaxScaler
from joblib import dump, load
from os import path

class Training:
    __model = None
    __scalerInput = MinMaxScaler()
    __scalerOutput = MinMaxScaler()

    def __init__(self, filename):
        self.__loadModel(filename)

    def train(self, history):
        times, tradeY = zip(*history.items())
        smoothData = Kalman(history).getSmoothData()

        inputData = []
        outputData = []
        countTimes = len(times)
        countPredicts = len(predictionIntervals)
        countDatum = predictPeriod / scanInterval

        for timeIndex, timestamp in enumerate(times):
            datum = [smoothData[timeIndex]]
            dataIndex = timeIndex + 1
            while dataIndex < countTimes and len(datum) <= countDatum:
                datum.append(smoothData[dataIndex])
                dataIndex += 1

            predictCounter = 0

            if dataIndex < countTimes:
                startPredictTimestamp = times[dataIndex]
                predict = []

                while dataIndex < countTimes and predictCounter < countPredicts:
                    if times[dataIndex] >= startPredictTimestamp + predictionIntervals[predictCounter]:
                        predict.append(smoothData[dataIndex])
                        predictCounter += 1

                    dataIndex += 1

                if predictCounter != countPredicts:
                    if predictCounter > 0:
                        for index in range(predictCounter, countPredicts):
                            predict.append(predict[-1])

                    else:
                        for index in range(0, countPredicts):
                            predict.append(datum[-1])

                if len(datum) == 0:
                    continue

                if len(datum) < countDatum:
                    for index in range(len(datum), countDatum):
                        datum.append(datum[-1])

                inputData.append(datum)
                outputData.append(predict)

        if len(inputData) == 0 or len(inputData) != len(outputData):
            print("Have not data for training")

        else:
            self.__scalerInput.fit(inputData)
            self.__scalerOutput.fit(outputData)

            inputData  = DataFrame(self.__scalerInput.transform(inputData),  dtype = float)
            outputData = DataFrame(self.__scalerOutput.transform(outputData), dtype = float)

            try:
                self.__model = neural_network.MLPRegressor(solver = "lbfgs", activation = 'logistic', max_iter = 1000000)

                self.__model.fit(inputData, outputData)

                print("Learn score = ", self.__model.score(inputData, outputData))

                #print(outputData[:3], self.__model.predict(inputData[:3]))
            except Exception as message:
                self.__model = None
                print("ERROR WHEN CREATE TRADE MODEL: " + str(message))

    def tradePredict(self, dayValues, nowTime):
        countInputValues = len(dayValues)

        try:
            countExpectedValues = self.__scalerInput.n_features_in_
            if self.__model is not None and countInputValues > 0:
                if countInputValues > countExpectedValues:
                    dayValues = dayValues[countInputValues - countExpectedValues:]
                elif countInputValues < countExpectedValues:
                    for i in range(0, countExpectedValues - countInputValues):
                        dayValues.insert(0, dayValues[0])

                inputData = DataFrame(self.__scalerInput.transform([dayValues]), dtype = float)

                outputData = self.__model.predict(inputData)
                outputData = self.__scalerOutput.inverse_transform(outputData)

                result = {}

                if len(outputData) > 0:
                    for index, time in enumerate(predictionIntervals):
                        result[nowTime + time] = outputData[0][index]

                    return result
        except:
            pass

        return None


    def saveModel(self, filename):
        if self.__model is not None:
            with open(filename + ".model", 'wb') as saveFile:
                dump(self.__model, saveFile)

            with open(filename + ".input", 'wb') as saveFile:
                dump(self.__scalerInput, saveFile)

            with open(filename + ".output", 'wb') as saveFile:
                dump(self.__scalerOutput, saveFile)


    def __loadModel(self, filename):
        if path.isfile(filename + ".model"):
            with open(filename + ".model", 'rb') as loadFile:
                self.__model = load(loadFile)

        if path.isfile(filename + ".input"):
            with open(filename + ".input", 'rb') as loadFile:
                self.__scalerInput = load(loadFile)

        if path.isfile(filename + ".output"):
            with open(filename + ".output", 'rb') as loadFile:
                self.__scalerOutput = load(loadFile)


