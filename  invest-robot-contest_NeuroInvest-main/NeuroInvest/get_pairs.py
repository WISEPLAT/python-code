from os import path
from time import time

pairsFile = "api-cache/pairs.json"

if not path.isfile(pairsFile) or int(time()) - path.getmtime(pairsFile) > 5 * 60:
    import json
    from trade_tuples import tradesTuple
    pairs = []
    for tradeTuple in tradesTuple:
        pairs.append(tradeTuple.getName())

    with open(pairsFile, 'w') as file:
        json.dump(pairs, file)

#with open(pairsFile, 'r') as file:
#    print(file.read())

