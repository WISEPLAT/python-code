import asyncio
import os
from datetime import timedelta

from tinkoff.invest import AsyncClient, CandleInterval
from tinkoff.invest.utils import now
import matplotlib.pyplot as plt
candels_g = []
candels_r = []
candels_k = []
nomers_g = []
nomers_r = []
nomers_k = []
candels = []
cans = []
take_profit = 0.058
stop_los = 1.18
nomer=0
pos = 1
plt.ion()
TOKEN = ""
async def main():
    global nomer
    global pos
    global otkitie
    global nomers_g
    global nomers_r
    global nomers_k
    global candels_g
    global candels_r
    global candels_k
    global cans
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            #id акции
            figi="BBG000B9XRY4",
            #время
            from_=now() - timedelta(days=10),
            #промежуток
            interval=CandleInterval.CANDLE_INTERVAL_5_MIN,
        ):
            #вывод
            low = float(candle.low.units)+(float(candle.low.nano)*0.000000001)
            hight = float(candle.high.units)+(float(candle.high.nano)*0.000000001)
            cena = low+((hight-low)/2)
            candels.append(cena)
            if take_profit>stop_los:
                if nomer ==0:
                    otkitie = candels[0]
                    plt.plot([0], [candels[0]], 'ro',color="k")
                if pos ==1:
                    if cena <= otkitie-stop_los:
        #g продажа на повышение
                        nomers_g.append(nomer)
                        candels_g.append(cena)
                        pos =2
                    if cena >= otkitie+stop_los:
        #r продажа на понижение
                        nomers_r.append(nomer)
                        candels_r.append(cena)
                        pos =3
                if pos ==2:
        #k продать на понижение
                    if cena <= otkitie-take_profit:
                        nomers_k.append(nomer)
                        candels_k.append(cena)
                        pos =1
                        otkitie=cena
                        print("+")
                    elif cena >= otkitie+stop_los:
                        nomers_k.append(nomer)
                        candels_k.append(cena)                    
                        pos =1
                        otkitie=cena
                        print("-")
        #k продать на повыщение
                if pos ==3:
                    if cena >= otkitie+take_profit:
                        nomers_k.append(nomer)
                        candels_k.append(cena)                    
                        pos =1
                        otkitie=cena
                        print("+")
                    elif cena <= otkitie-stop_los:
                        nomers_k.append(nomer)
                        candels_k.append(cena)                    
                        pos =1
                        otkitie=cena
                        print("-")
            elif take_profit<stop_los:
                if nomer ==0:
                    otkitie = candels[0]
                    plt.plot([0], [candels[0]], 'ro',color="k")
                if pos ==1:
                    if cena >= otkitie+take_profit:
        #g продажа на повышение
                        nomers_g.append(nomer)
                        candels_g.append(cena)
                        pos =2
                    if cena <= otkitie-take_profit:
        #r продажа на понижение
                        nomers_r.append(nomer)
                        candels_r.append(cena)
                        pos =3
                if pos ==2:
        #k продать на понижение
                    if cena <= otkitie-take_profit:
                        nomers_k.append(nomer)
                        candels_k.append(cena)
                        pos =1
                        otkitie=cena
                        print("+")
                    elif cena >= otkitie+stop_los:
                        nomers_k.append(nomer)
                        candels_k.append(cena)                    
                        pos =1
                        otkitie=cena
                        print("-")
        #k продать на повыщение
                if pos ==3:
                    if cena >= otkitie+take_profit:
                        nomers_k.append(nomer)
                        candels_k.append(cena)                    
                        pos =1
                        otkitie=cena
                        print("+")
                    elif cena <= otkitie-stop_los:
                        nomers_k.append(nomer)
                        candels_k.append(cena)                    
                        pos =1
                        otkitie=cena
                        print("-")
            plt.clf()
            plt.plot(nomers_g, candels_g,'ro',color='g')
            plt.plot(nomers_r, candels_r,'ro',color='r')
            plt.plot(nomers_k, candels_k,'ro',color='k')
            plt.plot(candels)
            plt.draw()
            plt.gcf().canvas.flush_events()
            nomer+=1
if __name__ == "__main__":
    asyncio.run(main())
    #plt.axhline(y=(otkitie-mal),color="r")
    #plt.axhline(y=(otkitie+mal),color="b")
    #plt.axhline(y=(otkitie-bol),color="b")
    #plt.axhline(y=(otkitie+bol),color="r")
    #plt.axhline(y=(otkitie),color="k")
    plt.ioff()
    plt.show()