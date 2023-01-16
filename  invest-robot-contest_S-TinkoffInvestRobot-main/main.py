import tkinter as tk
from datetime import datetime
from tinkoff.invest import *
from tinkoff.invest import Client, RequestError
import time
from tinkoff.invest.services import SandboxService
import threading
def high():
    global accaunt
    global figi
    global r
    global end_bal
    try:
        with Client(TOKEN) as client:
            do_pokypki = len(client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions)
            r = client.sandbox.post_sandbox_order(
                figi=figi,
                quantity=1,
                account_id=accaunt,
                order_id=datetime.now().strftime("%T-%m-%dT %H:%M:%S"), 
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
            p = True
            while p:
                time.sleep(1)
                try:
                    if(len(client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions))>do_pokypki:
                        end_bal = client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions[0].quantity.units+client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions[0].quantity.nano*0.000000001
                        p=False
                except:
                    pass
    except:return(high)
def high_sell():
    print("продали акцию")
    global accaunt
    global figi
    try:
        with Client(TOKEN) as client:
            do_pokypki = len(client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions)
            r = client.sandbox.post_sandbox_order(
                figi=figi,
                quantity=1,
                price=Quotation(units=126,nano=0),
                account_id=accaunt,
                order_id=datetime.now().strftime("%T-%m-%dT %H:%M:%S"),
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_LIMIT
            )
        p = True
        while p:
            time.sleep(1)
            try:
                if(len(client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions))>do_pokypki:
                    p=False
            except:
                pass
    except:return(high_sell)
def low():
    global TOKEN
    global price 
    global comissia
    with Client(TOKEN) as client:
        lol = int(price.last_prices[0].price.units*comissia)
        cost = int(price.last_prices[0].price.nano*comissia)
        client.sandbox.sandbox_pay_in(account_id = accaunt,amount=MoneyValue(units=lol,nano=int(cost),currency="usd"))
def low_sell():
    global TOKEN
    global price 
    global comissia
    with Client(TOKEN) as client:
        lol = int(price.last_prices[0].price.units*comissia)
        cost = int(price.last_prices[0].price.nano*comissia)
        client.sandbox.sandbox_pay_in(account_id = accaunt,amount=MoneyValue(units=lol,nano=int(cost),currency="usd"))
def str():
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
    global figi
    global end_bal
    global TOKEN
    global accaunt
    global r
    global price 
    global comissia
    for i in range(2000):
        time.sleep(1)
        print(i)
        with Client(TOKEN) as client:
            try:
                price = client.market_data.get_last_prices(figi=[figi])
                cena = price.last_prices[0].price.units+price.last_prices[0].price.nano*0.000000001
                vremia = price.last_prices[0].time.year,price.last_prices[0].time.month,price.last_prices[0].time.day,price.last_prices[0].time.hour,price.last_prices[0].time.minute,price.last_prices[0].time.second,price.last_prices[0].time.microsecond
                grafs.append(cena)
                print(cena)
                if take_profit>stop_los:
                    if nomer ==0:
                        start_bal=client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions[0].quantity.units+client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions[0].quantity.nano*0.000000001
                        otkitie = grafs[0]
                        #покупка на повышение
                        th1 = threading.Thread(target = high)
                        th1.start()
                        #покупка на понижение
                        comissia = abs(((start_bal- end_bal)-(r.total_order_amount.units+r.total_order_amount.nano*0.000000001))/(r.total_order_amount.units+r.total_order_amount.nano*0.000000001)*100)
                        th6 = threading.Thread(target = low)
                        th6.start()
                        
                    if pos ==1:
                        if cena <= otkitie-stop_los:
            #g продажа на повышение
                            nomers_g.append(nomer)
                            candels_g.append(cena)
                            pos =2
                            th15 = threading.Thread(target = high_sell)
                            th15.start()
                            print("продали длинную")
                        if cena >= otkitie+stop_los:
            #r продажа на понижение
                            nomers_r.append(nomer)
                            candels_r.append(cena)
                            pos =3
                            try:
                                th11 = threading.Thread(target = low_sell)
                                th11.start()
                            except:
                                pass
                            print("продали короткую")
                    if pos ==2:
            #k продать на понижение
                        if cena <= otkitie-take_profit:
                            nomers_k.append(nomer)
                            candels_k.append(cena)
                            pos =1
                            otkitie=cena
                            try:
                                th12 = threading.Thread(target = low_sell)
                                th12.start()
                            except:
                                pass
                            print("продали короткую")
                            th2 = threading.Thread(target = high)
                            th2.start()
                            th7 = threading.Thread(target = low)
                            th7.start()
                            print("+")
                            print("купили 2")
                        elif cena >= otkitie+stop_los:
                            nomers_k.append(nomer)
                            candels_k.append(cena)                    
                            pos =1
                            otkitie=cena
                            try:
                                th13 = threading.Thread(target = low_sell)
                                th13.start()
                            except:
                                pass
                            print("продали короткую")
                            th3 = threading.Thread(target = high)
                            th3.start()
                            try:
                                th8 = threading.Thread(target = low)
                                th8.start()
                            except:
                                pass
                            print("-")
                            print("купили 2")
            #k продать на повыщение
                    if pos ==3:
                        if cena >= otkitie+take_profit:
                            nomers_k.append(nomer)
                            candels_k.append(cena)                    
                            pos =1
                            otkitie=cena
                            th16 = threading.Thread(target = high_sell)
                            th16.start()
                            print("продали длинную")
                            th4 = threading.Thread(target = high)
                            th4.start()
                            try:
                                th9 = threading.Thread(target = low)
                                th9.start()
                            except:
                                pass
                            print("+")
                            print("купили 2")
                        elif cena <= otkitie-stop_los:
                            nomers_k.append(nomer)
                            candels_k.append(cena)                    
                            pos =1
                            otkitie=cena
                            th17 = threading.Thread(target = high_sell)
                            th17.start()
                            print("продали длинную")
                            th5 = threading.Thread(target = high)
                            th5.start()
                            try:
                                th10 = threading.Thread(target = low)
                                th10.start()
                            except:
                                pass
                            print("-")
                            print("купили 2")
            except:
                pass
#стратегия
def strotegy():
    global window
    window.destroy()
    window =  tk.Tk()
    with Client(TOKEN) as client:
        r = client.sandbox.get_sandbox_accounts().accounts
        for i in range(len(r)):
            tk.Button(
            text=r[i].id,
            command=lambda i=r[i].id:figi_com(i), 
            height = 4, 
            width =30).pack()
    window.mainloop()
def stop_win():
    global window
    global TOKEN
    global accaunt
    but_1.pack_forget()
    with Client(TOKEN) as client:
        balance = client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions[0].quantity
    text_balance = tk.Label(text=balance)
    text_balance.pack()
    tk.Button(text="stop").pack()
    for i in range(10000):
        time.sleep(1)
        with Client(TOKEN) as client:
            text_balance['text'] = client.sandbox.get_sandbox_portfolio(account_id=accaunt).positions[0].quantity
def plts():
    global col
    global figi
    global window
    global figi
    global accaunt
    global col
    global TOKEN
    global grafs
    global stop_los
    global take_profit
    global candels_g
    global candels_r
    global candels_k
    global nomer
    global nomers_g
    global nomers_k
    global nomers_r
    global pos
    grafs = []
    stop_los = 0.5 ##################################
    take_profit = 1 ##################################
    candels_g = []
    candels_r = []
    candels_k = []
    nomers_g = []
    nomers_r = []
    nomers_k = []
    nomer=0
    pos = 1
    th1 = threading.Thread(target = stop_win)
    th1.start()
    time.sleep(1)
    th = threading.Thread(target = str)
    th.start()
def col_vo(j):
    #figi
    global col
    global figi
    global window
    global but_1
    window.destroy()
    print(j)
    figi = j
    window =  tk.Tk()
    th1 = threading.Thread(target = plts)
    but_1 = tk.Button(text=1,height = 4, 
            width =30,command=lambda:[th1.start()])
    but_1.pack()
    col = 1
    window.mainloop()
def figi_com(i):
    #acc
    global accaunt
    global figis
    accaunt = i
    figis = [["google","apple"],["BBG009S3NB30","BBG000B9XRY4"]]
    global window
    window.destroy()
    window =  tk.Tk()
    for k in range(len(figis[0])):
        tk.Button(
            text=figis[0][k],
            command=lambda j=figis[1][k]:col_vo(j), 
            height = 4, 
            width =30).pack()
    window.mainloop()
    window.mainloop()
    
    
    
    
#аккаунт
def creat():
    global TOKEN
    with Client(TOKEN) as client:
        x = client.sandbox.open_sandbox_account()
        id_ac = x.account_id #номер аккаунта
        client.sandbox.sandbox_pay_in(account_id = id_ac,amount=MoneyValue(units=1000000,nano=0,currency="usd"))#пополнение счёта
        print(client.sandbox.sandbox_pay_in(account_id = id_ac)) #вывод денег
    print("аккаунт создан")
def remove():
    with Client(TOKEN) as client:
        r = client.sandbox.get_sandbox_accounts().accounts
        for i in range(len(r)):
            client.sandbox.close_sandbox_account(account_id=r[i].id)
    print("аккаунты удалены")
def lists():
    print("список аккаунтов")
    with Client(TOKEN) as client:
        r = client.sandbox.get_sandbox_accounts().accounts
        for i in range(len(r)):
            print(r[i])
def profil():
    global window
    window.destroy()
    window =  tk.Tk()
    
    button_acc = tk.Button(
    text="создать аккаунт",
    command=creat, 
          height = 8, 
          width = 30)
    button_accs = tk.Button(
    text="список аккаунтов",
    command=lists, 
          height = 8, 
          width = 30)
    button_acc_rem = tk.Button(
    text="удалить аккаунты",
    command=remove, 
          height = 8, 
          width = 30)
    button_bac = tk.Button(
    text="назад",
    command=token_com, 
          height = 8, 
          width = 30)
    button_bac.pack()
    button_acc_rem.pack()
    button_accs.pack()
    button_acc.pack()
    
    window.mainloop()
    
#назад
def back():
    global window
    window.destroy()
    main()
#главная
def token_com():
    global window
    global TOKEN
    TOKEN = entry.get()
    window.destroy()
    window =  tk.Tk()
    
    button1 = tk.Button(
    text="профиль",
    command=profil, 
          height = 8, 
          width = 30
    )
    button2 = tk.Button(
    text="стратегия",
    command=strotegy, 
          height = 8, 
          width = 30
    )
    button3 = tk.Button(
    text="назад к токену",
    command=back, 
          height = 8, 
          width = 30
    )
    button1.pack()
    button2.pack()
    button3.pack()
    
    window.mainloop()
#токен
def main():
    global entry
    global window
    window =  tk.Tk()
    entry = tk.Entry(width = 35)
    button = tk.Button(
        text="Нажми на меня!",
        command=token_com, 
          height = 8, 
          width = 30
    )
    entry.pack()
    button.pack()
    window.mainloop()
main()