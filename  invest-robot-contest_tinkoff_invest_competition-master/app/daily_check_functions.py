import pandas as pd
import tinvest as ti
from openapi_client import openapi
#import yfinance as yf
import datetime
from datetime import timedelta
import pytz
import time
import telebot
from telebot import types
import sys
import time
import traceback
import config
import parameters_of_trading
import os


bot = telebot.TeleBot(config.telegram_bot_id())
client = ti.SyncClient(config.token_tinkoff_invest())
client2 = openapi.api_client(config.token_tinkoff_invest())


class CheckRobot2_0:
    "Класс проверяющий текущие ордера"
    def __init__(self, address_of_orders, index_of_process):
        self.address_of_orders = address_of_orders
        self.index_of_process = index_of_process
        self.chat_id = config.telegram_сhat_id()
        self.send = ''
        self.position = 0
        self.price = 500
        
    "Отсылка сообщений в tg бот"
    def message_alarm(self):
        if self.index_of_process == 1:
            self.send = 'Нет открытых позиций, робот готов к покупке ' + str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S"))
        try:
            bot.send_message(self.chat_id, self.send)
        except:
            print(str(traceback.format_exc()))
        
        
    """Получение всех ордеров"""            
    def get_all_orders(self):
        df_all_orders = pd.read_csv(self.address_of_orders, names = ['time','figi','price','type','order_id','status'])
        df_all_orders['time'] = pd.to_datetime(df_all_orders['time'], format="%Y_%m_%d-%H:%M:%S")
        
        """Максимальное значение времени по ордеру ReallSell"""
        max_reallsell = df_all_orders[df_all_orders['type'] == 'ReallSell']
        time_ = list(max_reallsell[max_reallsell['time'] == max_reallsell['time'].max()]['time'])[0]
        df_all_orders = df_all_orders[df_all_orders['time'] > time_]
        if len(df_all_orders) == 0: 
            return -1
        else:
            return 1
    
    """Получение нужной позиции """
    def get_all_for_sell(self):     
        date_, figi, type_, price, quantity, currency, commission, payment, ticker = [],[],[],[],[],[],[],[],[]
        df_all_orders = pd.read_csv(self.address_of_orders, names = ['time','figi','price','type','order_id','status'])
        df_all_orders['time'] = pd.to_datetime(df_all_orders['time'], format="%Y_%m_%d-%H:%M:%S")
        
        """Максимальное значение времени по ордеру ReallSell"""
        max_reallsell = df_all_orders[df_all_orders['type'] == 'ReallSell']
        time_ = list(max_reallsell[max_reallsell['time'] == max_reallsell['time'].max()]['time'])[0]
        df_all_orders = df_all_orders[df_all_orders['time'] > time_]
        figi_ = list(df_all_orders['figi'])[0]
        tz = pytz.timezone('Europe/Moscow')
        date_start = datetime.datetime(time_.year, time_.month, time_.day, time_.hour-3, time_.minute, time_.second)
        date_start = pytz.utc.localize(date_start).astimezone(tz).isoformat()
        date_end = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
        date_end = pytz.utc.localize(date_end).astimezone(tz).isoformat()
        operat = client2.operations.operations_get(_from=date_start, to=date_end)
        
        for ind_ in range(len(operat.payload.operations)):
            try:
                ttype_ = operat.payload.operations[ind_].operation_type
                if (ttype_  == 'Sell') or (ttype_ == 'Buy'):
                    try:
                        type_.append(operat.payload.operations[ind_].operation_type)
                    except:
                        type_.append('NONE')
                    try:
                        date_.append(operat.payload.operations[ind_].date)
                    except:
                        date_.append('NONE')    
                    try:
                        commission.append(operat.payload.operations[ind_].commission.value)
                    except:
                        commission.append('NONE')    
                    try:
                        figi.append(operat.payload.operations[ind_].figi)
                    except:
                        figi.append('NONE')
                    try:
                        price.append(operat.payload.operations[ind_].price)
                    except:
                        price.append('NONE')
                    try:
                        quantity.append(operat.payload.operations[ind_].quantity)
                    except:
                        quantity.append('NONE')
                    try:
                        payment.append(operat.payload.operations[ind_].payment)
                    except:
                        payment.append('NONE') 
                    try:
                        currency.append(operat.payload.operations[ind_].currency)
                    except:
                        currency.append('NONE')    
                    try:
                        ticker.append(operat.payload.operations[ind_].status)
                    except:
                        ticker.append('NONE')
            except:
                continue


        df_all_orders_for_analysis = pd.DataFrame(
                            {'date': date_,
                             'commission': commission,
                             'figi': figi,
                             'price': price,
                             'quantity': quantity, 
                             'payment': payment,
                             'currency': currency,
                             'type': type_, 
                             'status': ticker
                            })
        df_all_orders_for_analysis = df_all_orders_for_analysis[df_all_orders_for_analysis['figi'] == figi_]
        df_all_orders_for_analysis['date2'] = df_all_orders_for_analysis['date'].apply(lambda x: x.timestamp())
        df_all_orders_for_analysis = df_all_orders_for_analysis[df_all_orders_for_analysis['date2'] >= (time_.timestamp()-3*3600)] #не разобрался с таймзоной - поэтому так лол ;)
        df_all_orders_for_analysis = df_all_orders_for_analysis[df_all_orders_for_analysis['status'] == 'Done']
        df_all_orders_for_analysis['total'] = df_all_orders_for_analysis['payment']/df_all_orders_for_analysis['price']
        df_all_orders_for_analysis['commission'] = df_all_orders_for_analysis['commission']*3
        return df_all_orders_for_analysis
    
    
    
class CheckRobotSellOrder:
    def __init__(self, profit_value, df_orders):
        self.profit_value = profit_value
        self.payment_list = list(df_orders['payment'])
        self.commission_list = list(df_orders['commission'])
        self.total_list = list(df_orders['total'].apply(lambda x: round(x, 1)))
        self.figi_ = list(df_orders['figi'])[0]
        self.payment = 0
        self.total = 0
        self.price = 0
        self.list_of_orders = []
        self.figis = []
        self.orders_for_potential_del = []
        self.output_value = 0
        self.del_post_orders = 0
        
    
    def make_do_order(self):
        for ind_ in range(len(self.total_list)):
            self.payment = self.payment + self.payment_list[ind_] + self.commission_list[ind_]
            self.total = self.total + self.total_list[ind_]
            
        if self.total != 0:
            self.list_of_orders = client.orders.orders_get().payload
            self.price = round((self.payment/self.total)*self.profit_value, 2)
            self.total = round(abs(self.total))
            for ind_ in range(len(self.list_of_orders)):
                if self.list_of_orders[ind_].figi == self.figi_:
                    self.figis.append(self.list_of_orders[ind_].figi)
                    self.orders_for_potential_del.append(self.list_of_orders[ind_].order_id)
                    
            if len(self.figis) == 0:
                self.output_value = 1
                return self.output_value, self.figi_, self.total, self.price, self.payment
            else:
                for order_id in self.orders_for_potential_del:
                    try:
                        client2.orders.orders_cancel_post(order_id=order_id)
                        self.del_post_orders+=1
                    except:
                        pass
                if self.del_post_orders == 0:
                    self.output_value = 0
                    self.figi_ = ''
                    self.total = 0
                    self.price = 0
                    return self.output_value, self.figi_, self.total, self.price, self.payment
                else:
                    self.output_value = 2
                    return self.output_value, self.figi_, self.total, self.price, self.payment
        else:
            self.output_value = -1
            self.price = 0
            return self.output_value, self.figi_, self.total, self.price, self.payment
        

class CheckRobotSellOrderAveraging:
    def __init__(self, address_of_positions, address_of_progons, price, position_limit, rsi_threshold, number_of_stocks):
        self.df_of_positions = pd.read_csv(address_of_positions, names = ['time','figi','price','type','order_id','status'])
        self.df_of_progons = pd.read_csv(address_of_progons, names = ['time', 'ticker', 'price', 'RSI', 'type'])
        self.price = price
        self.position_limit = position_limit
        self.rsi_threshold = rsi_threshold
        self.status_of_average = 0
        self.number_of_stocks = number_of_stocks
        
    
    def make_do_average_order(self):

        values, currency, balance, figi, ticker, name, evalue = [],[],[],[],[],[],[]
        self.df_of_positions['time'] = pd.to_datetime(self.df_of_positions['time'], format="%Y_%m_%d-%H:%M:%S")
        max_reallsell = self.df_of_positions[self.df_of_positions['type'] == 'ReallSell']
        time_ = list(max_reallsell[max_reallsell['time'] == max_reallsell['time'].max()]['time'])[0]
        self.df_of_positions = self.df_of_positions[self.df_of_positions['time'] > time_]
        length_ = len(list(self.df_of_positions['figi']))
        if length_ > 0:
            figi_ = list(self.df_of_positions['figi'])[0]
            pf = client.portfolio.portfolio_get()
            tick = client2.market.market_search_by_figi_get(figi_).payload.ticker
            for ind_ in range(len(pf.payload.positions)):
                if pf.payload.positions[ind_].figi == figi_: #figi_
                    values.append(pf.payload.positions[ind_].average_position_price.value)
                    currency.append(pf.payload.positions[ind_].average_position_price.value)
                    balance.append(pf.payload.positions[ind_].balance)
                    figi.append(pf.payload.positions[ind_].figi)
                    ticker.append(pf.payload.positions[ind_].ticker)
                    name.append(pf.payload.positions[ind_].name)
                    evalue.append(pf.payload.positions[ind_].expected_yield.value)
            portfolio = pd.DataFrame({
                'ticker': ticker,
                'name': name,
                'values': values,
                'balance': balance,
                'expected_value': evalue,
                'currency': currency,
                'figi': figi
            })
            portfolio['current_price'] = round((portfolio['values']*portfolio['balance'] + portfolio['expected_value'])/portfolio['balance'], 2)
            portfolio['position'] = portfolio['values']*portfolio['balance']
    
            curr_price = portfolio['current_price'][0]
            position = portfolio['position'][0]

            self.df_of_progons = self.df_of_progons[self.df_of_progons['ticker'] == tick]
            self.df_of_progons = self.df_of_progons.reset_index(drop = True)
            self.df_of_progons['ind_'] = self.df_of_progons.index
            self.df_of_progons = self.df_of_progons.sort_values(by = 'ind_',ascending=False)
            self.df_of_progons = self.df_of_progons[0:2]
            rsi_ = (list(self.df_of_progons['RSI'])[0] +list(self.df_of_progons['RSI'])[1])/2
            
            if position < self.position_limit and (100*(curr_price - self.price)/self.price) < -1 and rsi_ < self.rsi_threshold:
                """Очищаются все ордера на продажу по этому FIGI""" 
                del_post_orders = 0
                list_of_orders = list(self.df_of_positions[self.df_of_positions['type'] == 'Sell']['order_id'])
                for order_id in list_of_orders:
                    order_id = int(float(order_id))
                    try:
                        client2.orders.orders_cancel_post(order_id=order_id)
                        del_post_orders+=1
                    except:
                        pass
                
                if del_post_orders == 0:
                    self.status_of_average = -1
                    return self.status_of_average, figi_, self.number_of_stocks, curr_price
                else:
                    self.status_of_average = 1
                    return self.status_of_average, figi_, self.number_of_stocks, curr_price

            return self.status_of_average, figi_, self.number_of_stocks, curr_price
        
        
        else:
            figi_ = ''
            self.number_of_stocks = 0
            curr_price = 0
            return self.status_of_average, figi_, self.number_of_stocks, curr_price
        
        
        
        
class MakeBuyAverageOrder:
    def __init__(self, figi, lots_of_average, current_price, total, price, log_file_address, evalute_sell_price_after_average):
        self.figi = figi
        self.lots_of_average = lots_of_average
        self.current_price = current_price
        """Старые значения величин позиций и цен"""
        self.total = total
        self.price = price
        self.log_file_address = log_file_address
        self.sell_price = evalute_sell_price_after_average
    
    def make_order_average_buy(self):
        order_response = client2.orders.orders_limit_order_post(figi = figi, limit_order_request={"lots": self.lots_of_average, "operation": 'Buy', "price": self.current_price})
        """Задержка в минуту для возможного исполнения ордера"""
        time.sleep(60)
        try:
            order_list, status_list, operation_list, figi_list = [],[],[],[]
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
        except:
            """Делалась ранее задержка в 10 секунд для потенциального обновления API - на тестах 
            были случаи когда ордера не успевали обновиться"""
            time.sleep(10)
            order_list, status_list, operation_list, figi_list = [],[],[],[]
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
            """Ecли ордер не смог выполниться - удаляем ордер"""
            client2.orders.orders_cancel_post(order_id=order_response.payload.order_id)
            """И тут же ставим ордер на продажу по старому объему акций """        
            order_response_sell = client2.orders.orders_limit_order_post(figi = self.figi, limit_order_request={"lots": self.total, "operation": 'Sell', "price": self.price})      
            f = open(self.log_file_address, 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(round(self.price, 2)) + ',' + 'Sell' + ',' + str(order_response_sell.payload.order_id) + ',' + str(order_response_sell.payload.status)))
            f.write('\n')
            f.close()
            
        else:
            """Если ордер исполнился - логгируем покупку"""
            f = open(self.log_file_address, 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(self.current_price) + ',' + 'Buy' + ',' + str(order_response.payload.order_id) + ',' + str(order_response.payload.status)))
            f.write('\n')
            f.close()
            """Высчитываем нужную цену продажи и ставим условие на продажу и логгируем продажу"""
            order_response_sell = client2.orders.orders_limit_order_post(figi = self.figi, limit_order_request={"lots": (self.total + self.lots_of_average), "operation": 'Sell', "price": self.sell_price})      
            f = open(self.log_file_address, 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(sell_price) + ',' + 'Sell' + ',' + str(order_response_sell.payload.order_id) + ',' + str(order_response_sell.payload.status)))
            f.write('\n')
            f.close()

    
    
class MakeOrders:
    def __init__(self, value, figi, total, price, order_response_sell, log_file_address):
        self.value = value
        self.figi = figi
        self.total = total
        self.price = price
        self.chat_id = config.telegram_сhat_id()
        self.send = 0
        self.order_response_sell = order_response_sell
        self.log_file_address = log_file_address
    
    def update_data_and_send_to_bot(self):
        if self.value == 0:
            self.send = 'Не удалось удалить ни одного ордера - код завершен с ошибкой'
        elif self.value == -1:
            self.send = 'TradeSucsess - profit: ' + str(self.price)
            f = open(self.log_file_address, 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(round(self.price, 2)) + ',' + 'ReallSell' + ',' + str(11111) + ',' + str('tradeSucsess')))
            f.write('\n')
            f.close()
        elif self.value == 1:
            self.send = 'Начальный ордер поставлен:' + ' ' + str(self.order_response_sell.payload.status)
            f = open(self.log_file_address, 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(round(self.price, 2)) + ',' + 'Sell' + ',' + str(self.order_response_sell.payload.order_id) + ',' + str(self.order_response_sell.payload.status)))
            f.write('\n')
            f.close()
        elif self.value == 2:
            self.send = 'Послеусредненный ордер поставлен:' + ' ' + str(order_response_sell.payload.status)
            f = open(self.log_file_address, 'a+', encoding='utf-8')
            f.write(str(datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + ',' + str(self.figi) + ',' + str(round(self.price, 2)) + ',' + 'Sell' + ',' + str(self.order_response_sell.payload.order_id) + ',' + str(self.order_response_sell.payload.status)))
            f.write('\n')
            f.close()
        
        try:
            bot.send_message(self.chat_id, self.send)
        except:
            print(str(traceback.format_exc()))


