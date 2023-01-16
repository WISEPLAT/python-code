from os import path
from time import time

pairsDataFile = "api-cache/pairs_data.json"

if not path.isfile(pairsDataFile) or int(time()) - path.getmtime(pairsDataFile) > 5 * 60:
    import json
    from trade_tuples import tradesTuple
    pairsData = {}
    for tradeTuple in tradesTuple:
        tradeTuple.update()
        dayData = tradeTuple.getMomentData()
        if dayData is not None:
            pairsData[tradeTuple.getName()] = dayData

    with open(pairsDataFile, 'w') as file:
        json.dump(pairsData, file)

#with open(pairsDataFile, 'r') as file:
#    print(file.read())

