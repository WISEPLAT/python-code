from tinkoff.invest import *
from tinkoff.invest import Client, RequestError
import time
import matplotlib.pyplot as plt

TOKEN = ""
def acc():
    global id_ac
    with Client(TOKEN) as client:
        client.sandbox.open_sandbox_account()
        id_ac = client.sandbox.open_sandbox_account().account_id #номер аккаунта
        client.sandbox.sandbox_pay_in(account_id = id_ac,amount=MoneyValue(units=1000000,nano=0,currency="rub"))#пополнение счёта
        print(client.sandbox.sandbox_pay_in(account_id = id_ac)) #вывод денег
acc()
grafs = []
stop_los = 1.18
take_profit = 0.058 
candels_g = []
candels_r = []
candels_k = []
nomers_g = []
nomers_r = []
nomers_k = []
nomer=0
pos = 1
plt.ion()
def main():
    global stop_los
    global nomer
    global pos
    global take_profit
    global nomers_g
    global nomers_r
    global nomers_k
    global candels_g
    global candels_r 
    global candels_k
    for i in range(2000):
        time.sleep(1)
        print(i)
        with Client(TOKEN) as client:
            try:
                price = client.market_data.get_last_prices(figi=["BBG000B9XRY4"])
                cena = price.last_prices[0].price.units+price.last_prices[0].price.nano*0.000000001
                vremia = price.last_prices[0].time.year,price.last_prices[0].time.month,price.last_prices[0].time.day,price.last_prices[0].time.hour,price.last_prices[0].time.minute,price.last_prices[0].time.second,price.last_prices[0].time.microsecond
                grafs.append(cena)
                if take_profit>stop_los:
                    if nomer ==0:
                        otkitie = grafs[0]
                        plt.plot([0], [grafs[0]], 'ro',color="k")
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
                        otkitie = grafs[0]
                        plt.plot([0], [grafs[0]], 'ro',color="k")
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
                plt.plot([0], [grafs[0]], 'ro',color="k")
                plt.plot(nomers_g, candels_g,'ro',color='g')
                plt.plot(nomers_r, candels_r,'ro',color='r')
                plt.plot(nomers_k, candels_k,'ro',color='k')
                plt.plot(grafs)
                plt.draw()
                plt.gcf().canvas.flush_events()
                nomer+=1
            except:
                pass
if __name__ == "__main__":
    main()
    plt.ioff()
    plt.show()