import daily_check_functions
import daily_buy_functions
import config
import parameters_of_trading
import schedule
import time 
import pandas as pd
import datetime

    
def robot_day_traider():
    directory = '/files/'
    order_for_sale = daily_check_functions.CheckRobot2_0(directory + 'test_steven_cat.txt', 0).get_all_orders()
    if order_for_sale == -1:
        daily_check_functions.CheckRobot2_0(directory + 'test_steven_cat.txt', 1).message_alarm()
    elif order_for_sale == 1:
        df_all_orders_for_analysis = daily_check_functions.CheckRobot2_0(directory + 'test_steven_cat.txt', 0).get_all_for_sell()
        output_value, figi_, total, price, payment = daily_check_functions.CheckRobotSellOrder(parameters_of_trading.profit_value(), df_all_orders_for_analysis).make_do_order()
    
        if output_value == 0:
            daily_check_functions.MakeOrders(output_value, figi_, total, price, order_response_sell = '', log_file_address = directory + 'test_steven_cat.txt').update_data_and_send_to_bot()
        elif output_value == 1:
            order_response_sell = client2.orders.orders_limit_order_post(figi = figi_, limit_order_request={"lots": total, "operation": 'Sell', "price": price})
            daily_check_functions.MakeOrders(output_value, figi_, total, price, order_response_sell, log_file_address = directory + 'test_steven_cat.txt').update_data_and_send_to_bot()
        elif output_value == 2:
            order_response_sell = client2.orders.orders_limit_order_post(figi = figi_, limit_order_request={"lots": total, "operation": 'Sell', "price": price})
            daily_check_functions.MakeOrders(output_value, figi_, total, price, order_response_sell, log_file_address = directory + 'test_steven_cat.txt').update_data_and_send_to_bot()  
        elif output_value == -1:
            daily_check_functions.MakeOrders(output_value, figi_, total, price, order_response_sell = '', log_file_address = directory + 'test_steven_cat.txt').update_data_and_send_to_bot()
        """Возможное добавление усреднений"""
        if total != 0:
            number_of_stocks = parameters_of_trading.position_of_stocks(price, limit_of_step) 
            status_of_potential_average, figi_, number_of_stocks, curr_price = daily_check_functions.CheckRobotSellOrderAveraging(address_of_positions = directory + 'test_steven_cat.txt', address_of_progons = directory + 'all_progons.txt', price = price, position_limit = parameters_of_trading.limit_all_position(), rsi_threshold = parameters_of_trading.limit_rsi_on_stock(), number_of_stocks = number_of_stocks).make_do_average_order()
            if status_of_potential_average == 1:
                sell_price_after_average = parameters_of_trading.sell_after_average_price_evalute(parameters_of_trading.profit_value(), price, payment, total, parameters_of_trading.limit_of_step_average())
                MakeBuyAverageOrder(figi = figi_, lots_of_average = number_of_stocks, current_price = curr_price, total = total, price = price, log_file_address = log_file_address, evalute_sell_price_after_average = sell_price_after_average).make_order_average_buy()
                
                
def robot_buy_traider(limit_ticker):
    directory = '/files/'
    figi, ticker, avg_threshold, avg_RSI, price, index_quantille, index_quantille2, min_price_tendention, param_frequency, first_buy_flg  = RobotSearcherAndFirstBuy(limit_ticker = limit_ticker, directory = directory).daily_searcher()
    if first_buy_flg == 'FirstBuyCondition':
        lots = parameters_of_trading.lots_of_first_buy(price)
        FirstBuyBot(figi = figi, lots = lots, price = price, directory = directory).potential_first_buy()
    



if __name__ == '__main__':   
    
    
    """Выгрузка DataFrame по нужным тикерам по дню"""
    limit_ticker = pd.read_csv('/files/df_of_possible_tickers.txt')
    """Утренняя постановка ордера на премаркете"""
    robot_day_traider()
    while True:
        if datetime.datetime.now().hour <= 17:
            """Ждать каждые 5 минут до начала основной сессии + 30 минут (30 минут берется для дисбаланса рынка и для времени 
            расчета min_price_tendention"""
            time.sleep(5*60)
        else:
            schedule.every().day.at('23:05').do(parameters_of_trading.exit)
            schedule.every(6).minutes.do(robot_day_traider)
            schedule.every(5).minutes.do(robot_buy_traider)
            while True:
                schedule.run_pending()

                
                
                
                
                


