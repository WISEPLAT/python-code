import os
import datetime
from typing import List, Tuple
import pandas as pd
import tinvest as ti
from datetime import timedelta
from openapi_client import openapi
from talib import RSI, BBANDS
import statistics
import random
import telebot
from telebot import types
import numpy as np
import time
from pytz import timezone
import parameters_of_trading
import config


bot = telebot.TeleBot(config.telegram_bot_id())
client = ti.SyncClient(config.token_tinkoff_invest())
client2 = openapi.api_client(config.token_tinkoff_invest())


class RobotSearcherAndFirstBuy:
    def __init__(self, limit_ticker, directory):
        self.limit_ticker = limit_ticker
        self.list_of_Limit = list(self.limit_ticker['Limit'])
        self.list_of_ticker = list(self.limit_ticker['ticker'])
        self.list_of_figi = list(self.limit_ticker['figi'])
        self.list_of_Position = list(self.limit_ticker['Position'])
        self.list_of_threshold = list(self.limit_ticker['AVG_RSI_of_ticker'])
        self.list_of_RSI_alarm = list(self.limit_ticker['AVG_RSI_of_005'])
        self.list_of_percentage_of_ticker = list(self.limit_ticker['percentage'])
        self.list_of_tg_alarm = list(self.limit_ticker['AVG_RSI_of_05'])
        self.list_of_param_freq = list(self.limit_ticker['param_freq_parametr'])
        self.directory = directory
    
    def daily_searcher(self):
        list_of_orders = client2.orders.orders_get().payload
        figis = []
        for ind_ in range(len(list_of_orders)):
            figis.append(list_of_orders[ind_].figi)  
            
        for ind_ in range(len(self.list_of_Limit)):
            for day_ind_ in range(1, 8):
                df = parameters_of_trading.get_figi_data(self.list_of_figi[ind_], day_ind_)
                df.to_csv(self.directory + self.list_of_ticker[ind_] + '/'+str('day_history_') + str(day_ind_)+'.csv', index = False)        
            time.sleep(random.randint(1,4))
            list_of_files = os.listdir(self.directory + self.list_of_ticker[ind_] + '/')
            stock_df = pd.DataFrame()
            for file in list_of_files:
                try:
                    df = pd.read_csv(self.directory + self.list_of_ticker[ind_] + '/'+ file)
                    stock_df = pd.concat([stock_df, df])
                except:
                    pass
            stock_df = stock_df.sort_values(by = 'time', ascending = True)
            stock_df = stock_df.reset_index(drop = True)
            close = stock_df['c'].values
            rsi = RSI(close, timeperiod=23)
            rsi2 = list(rsi)
            rsi2.reverse()
            close = list(close)
            close.reverse()
            
            
            for_stat_list = rsi2[0:15]
            avg_RSI = statistics.mean(for_stat_list)
            avg_RSI = round(avg_RSI, 2)
        
        #now.hour - поменять время на 35 - пресессия/постсессия
        
            for_stat_list2 = rsi2[0:5]
            avg_RSI_for_threshold = statistics.mean(for_stat_list2)
            avg_RSI_for_threshold = round(avg_RSI_for_threshold, 2)
        
        
        #проверка недельки
            quantile_list = list(stock_df['c'].quantile(np.linspace(.1, 1, 10, 0)))
            price_ = close[0]
        
            index_quantille = 0
            for quantile_price in quantile_list:
                if quantile_price >= price_:
                    index_quantille = quantile_list.index(quantile_price)
                    break
                
            if index_quantille == 0:
                index_quantille = 10
               
            
            
        #проверка дня:
            stock_df2 = stock_df.copy()
            stock_df2['time'] = pd.to_datetime(stock_df2['time'])
            stock_df2 = stock_df2.sort_values(by = 'time', ascending = False)
            stock_df2 = stock_df2.reset_index(drop = True)
            stock_df2 = stock_df2[0:600]
        
            quantile_list2 = list(stock_df2['c'].quantile(np.linspace(.1, 1, 9, 0)))
            price_ = close[0]
        
            index_quantille2 = -1
            for quantile_price in quantile_list2:
                if quantile_price >= price_:
                    index_quantille2 = quantile_list2.index(quantile_price)
                    break
                
            if index_quantille2 == -1:
                index_quantille2 = 10 
        
            #такой функции нет - она скрыта из-за бизнес-логики)
            min_price_tendention = function(stock_df2['c'], quantile_list2[0], stock_df2['c'].min()) 
            
            
            hour_now = datetime.datetime.now().hour 
            
            if (avg_RSI < self.list_of_tg_alarm[ind_]) and (close[0] > min_price_tendention) and (index_quantille <= 10) and (index_quantille2 <= 10) and (self.list_of_param_freq[ind_] > parameters_of_trading.param_frequency_threshold()) and (hour_now >= 17) and (hour_now < 22):
                return self.list_of_figi[ind_], self.list_of_ticker[ind_], self.list_of_tg_alarm[ind_], avg_RSI, close[0], index_quantille, index_quantille2, min_price_tendention, self.list_of_param_freq[ind_], 'FirstBuyCondition'
            elif (avg_RSI < self.list_of_tg_alarm[ind_]):
                return self.list_of_figi[ind_], self.list_of_ticker[ind_], self.list_of_tg_alarm[ind_], avg_RSI, close[0], index_quantille, index_quantille2, min_price_tendention, self.list_of_param_freq[ind_], 'FirstBuyNoCondition'
            
            f = open(self.directory + 'all_progons.txt', 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + self.list_of_ticker[ind_]+ ',' + str(close[0]) + ',' + str(avg_RSI) + ',' + str(0)))
            f.write('\n')
            f.close()
        return self.list_of_figi[ind_], self.list_of_ticker[ind_], self.list_of_tg_alarm[ind_], avg_RSI, close[0], index_quantille, index_quantille2, min_price_tendention, self.list_of_param_freq[ind_], 'NoFirstBuy'

        
class FirstBuyBot:
    def __init__(self, figi, lots, price, directory):
        self.figi = figi
        self.lots = lots
        self.price = price
        self.directory = directory
        
    def potential_first_buy(self):
        df_of_status = pd.read_csv(self.directory + 'test_steven_cat.txt', names = ['time','figi','price','type','order_id','status'])
        df_of_status['time'] = pd.to_datetime(df_of_status['time'], format="%Y_%m_%d-%H:%M:%S")
        type_ = list(df_of_status[df_of_status['time'] == df_of_status['time'].max()]['type'])[0]

        if type_ == 'ReallSell': 
            order_list, status_list, operation_list, figi_list = [],[],[],[]
            order_response = client2.orders.orders_limit_order_post(figi = self.figi,
                                                               limit_order_request={"lots": self.lots,
                                                                                    "operation": 'Buy',
                                                                                    "price": self.price})

            """Ожидание исполнения ордера для позиции"""
            time.sleep(60)

            for ind_ in range(len(client2.orders.orders_get().payload)):
                order_list.append(client2.orders.orders_get().payload[ind_].order_id)
                status_list.append(client2.orders.orders_get().payload[ind_].status)
                operation_list.append(client2.orders.orders_get().payload[ind_].operation)
                figi_list.append(client2.orders.orders_get().payload[ind_].figi)
            df = pd.DataFrame({
                'order_id': order_list,
                'status': status_list,
                'operation': operation_list,
                'figi': figi_list
                })
    
            if len(df[df['order_id'] == str(order_response.payload.order_id)]) > 0:
                client2.orders.orders_cancel_post(order_id=order_response.payload.order_id)
            else:
                f = open(self.directory + 'test_steven_cat.txt', 'a+', encoding='utf-8')
                f.write(str(datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(self.price) + ',' + 'Buy' + ',' + str(order_response.payload.order_id) + ',' + str(order_response.payload.status)))
                f.write('\n')
                f.close()
                time.sleep(2)
        
                order_response_sell = client2.orders.orders_limit_order_post(figi = self.figi, limit_order_request={"lots": self.lots,
                                                                                     "operation": 'Sell',
                                                                                     "price": round(self.price*parameters_of_trading.first_time_profit_value(), 2)})
            
                f = open(self.directory + 'test_steven_cat.txt', 'a+', encoding='utf-8')
                f.write(str(datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(round(self.price*parameters_of_trading.first_time_profit_value(), 2)) + ',' + 'Sell' + ',' + str(order_response_sell.payload.order_id) + ',' + str(order_response_sell.payload.status)))
                f.write('\n')
                f.close()
        
        
        
        
