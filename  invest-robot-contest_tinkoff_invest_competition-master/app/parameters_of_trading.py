import sys
import pandas as pd 
import datetime
import tinvest as ti
from datetime import timedelta

client = ti.SyncClient(config.token_tinkoff_invest())


"""Профит-значение по позициям без учета комиссии"""
def profit_value():
    return 1.1

"""Лимит всех позиций"""
def limit_all_position():
    return 100

"""Лимит шага усреднения"""
def limit_of_step_average():
    return 10

"""Лимит по усредненному rsi_ в данной итерации универсален для всего трейдинга"""
def limit_rsi_on_stock():
    return 80

"""Величина позиции ордера - если цена больше лимита - покупка 1 акции, если меньше - рассчитывается
   величина позиции в акциях
"""        
def position_of_stocks(price, limit_of_average_step):
    if price > limit_of_average_step:
        return 1
    else:
        position = round(limit_of_average_step/price)
        return position
    
"""current_price*position_of_average - вычитается из-за особенностей расчета payment-а - последний ордер всегда не считается"""
def sell_after_average_price_evalute(profit_value, current_price, payment, position_of_stock_before, position_of_average):
    return round(profit_value*abs((payment - current_price*position_of_average)/(position_of_stock_before + position_of_average)),2)

"""Выход из day-trading - в 23-05"""
def exit():
    sys.exit()

"""Минутки для ежедневного серчинга"""
def get_figi_data(figi: str, i) -> pd.DataFrame:
    now = datetime.datetime.now()
    payload = client.get_market_candles(
        figi=figi,
        from_=now - timedelta(days=i),
        to=now - timedelta(days=i-1),
        interval=ti.CandleResolution.min1,
    ).payload
    return pd.DataFrame(c.dict() for c in payload.candles)

def param_frequency_threshold():
    return 1

"""First value"""
def first_time_profit_value():
    return 1.1


"""Первый заход в позицию"""
def lots_of_first_buy(price):
    if price > 90:
        return 1
    else:
        return round(90/price)



                 
