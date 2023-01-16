import sys
import os
from urllib import response

from grpc import services

path = os.getcwd()
repo_folder = os.path.dirname(os.path.dirname(path))
sys.path.append(repo_folder)
#!set PATH=%PATH%;%APPDATA%\Python\Scripts
#os.chdir(os.path.dirname(os.path.dirname(path)))

import logging
import time

from tinkoff.invest.mock_services import MockedClient
from decimal import Decimal
from tinkoff.invest.strategies.moving_average.strategy_settings import (
    MovingAverageStrategySettings,
)
from tinkoff.invest import CandleInterval, MoneyValue
from tinkoff.invest.strategies.moving_average.signal_executor import (
    MovingAverageSignalExecutor,
)
from tinkoff.invest.strategies.moving_average.supervisor import (
    MovingAverageStrategySupervisor,
)
from tinkoff.invest.strategies.moving_average.strategy_state import (
    MovingAverageStrategyState,
)
from tinkoff.invest.strategies.moving_average.strategy import MovingAverageStrategy
from tinkoff.invest.strategies.moving_average.trader import MovingAverageStrategyTrader
from datetime import timedelta, datetime, timezone
from tinkoff.invest.typedefs import ShareId, AccountId
from tinkoff.invest.strategies.base.account_manager import AccountManager
from tinkoff.invest.strategies.moving_average.plotter import (
    MovingAverageStrategyPlotter,
)

from tinkoff.invest import (
    CandleInstrument,
    InvestError,
    Client,
    InfoInstrument,
    SubscriptionInterval,
)

from tinkoff.invest.services import MarketDataStreamManager
from tinkoff.invest.services import MarketDataService
from tinkoff.invest import GetTradingStatusRequest

import my_account_manager
import my_trader
import my_strategy
import asyncio
import my_signal_executor


#Все даты учитываются по всемирному времени
def start_datetime() -> datetime:
    return datetime.now()

async def main(long_ma = 30, short_ma= 3, std_period = 22):

    TOKEN = os.environ["IIS_INVEST_TOKEN"]

    account_id = os.environ["INVEST_ACCOUNT_ID"]
   
    candle_interval = SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE

    default_stock = {"figi": "BBG004730ZJ9"}  #Акции ВТБ

    period = 1  # сюда добавить переход от tf к числу или отрекдактировать код снизу


    # Загружаем в робота настройки полученные из телеграмма. Наборы настроек для боевого робота и теста в песочнице одинаковые,
    # чтобы можно было их быстро применить после теста.
    # Настройки хранятся в словаре, для сохранения унификации кода с песочницей
    settings_data = {} 
    settings_data['default'] = {
        "stock":  default_stock,
        'long_ma' : long_ma, 
        'short_ma' : short_ma,
        'std_period' : std_period, #волотильность пока не учитывается в стратегии
        'tf' : candle_interval,
        'period' : period
    }
    
    set = 'default' #Ключ настроек робота, настройки хранятся в словаре, для сохранения унификации с песочницей

    figi = ShareId(settings_data[set]['stock']['figi']) 

   
    #Начнем логирование здесь:
    file_name = "Log_mov_aver__shortMA_%s, longMA_%s, stdP_%s,tf_%s.log" %(short_ma,long_ma, std_period, candle_interval) 
    logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO, filename = file_name)
    logger = logging.getLogger(__name__)

    logger.info(f'Инструмент =  {figi}')
    logger.info("Параметры Запуска робота _shortMA_%s, longMA_%s, stdP_%s,tf_%s.log" %(short_ma,long_ma, std_period,candle_interval))

    
    settings = MovingAverageStrategySettings(
        share_id=figi,  # figi конкретной ценной бумаги
        account_id=account_id,  # неважно для sandbox
        max_transaction_price=Decimal(
            200
        ),  # максимальный объем сделки - зависит от размера портфеля. сейчас фиксировано под Акции ВТБ
        candle_interval=settings_data[set]['tf'],  # тф - таймфрейм
        long_period=timedelta(minutes=settings_data[set]['long_ma'] * settings_data[set]['period']),  # длинная скользяшка
        short_period=timedelta(minutes=settings_data[set]['short_ma'] * settings_data[set]['period']),  # короткая скользяшка
        std_period=timedelta(minutes=settings_data[set]['std_period']  * settings_data[set]['period']),  # количество периодов для стд
    )
    

    k = 0

    my_app_name = "AndreiSoiko.tinkoffSDK" #Название приложения для участия в конкурсе

    start_balance_units = 0  

    with Client(TOKEN,app_name=my_app_name) as client:  #Присоединяемся к аккаунту для начала работы
        market_data_stream: MarketDataStreamManager = client.create_market_data_stream()
        
        #Подписываемся на информацию о свечах инструмента
        market_data_stream.candles.subscribe(
            [
                CandleInstrument(
                    figi,
                    interval=candle_interval,
                )
            ]
        )
        
        market_data_stream.info.subscribe(
            [default_stock]
        )

        #Позволяет получать информацию о состоянии счета
        account_manager = my_account_manager.AccountManager(
                services=client, strategy_settings=settings
            )

        #Объект хранит информацию о количестве позиций, которые должны быть открыты/закрыты роботом согласно сигналам стратегии
        state = MovingAverageStrategyState()

        #Сама стратегия, в которой проводит анализ данных рынка и генерирует сигналы
        strategy = my_strategy.MovingAverageStrategy(
                settings=settings,
                account_manager=account_manager,
                state=state,
            )

        #Объект, который накапливает полученные сигналы. В песочнице используется для дальнейшей визуализации. В рабочем режиме пока не используется
        supervisor = MovingAverageStrategySupervisor()
        

        #Объект, который обрабатывает полученные стратегией сигналы и выставляет ордера на биржу
        signal_executor = my_signal_executor.MovingAverageSignalExecutor(
                services=client,
                state=state,
                settings=settings,
        )

        #Объект, который собирает в себе все предыдущие объекты и ими управляет. Его метод trade() выполняет 1 такт торговли.
        moving_average_strategy_trader = my_trader.MovingAverageStrategyTrader(
                strategy=strategy,
                settings=settings,
                services=client,
                state=state,
                signal_executor=signal_executor,
                account_manager=account_manager,
                supervisor=supervisor,
            )

        
        #Зафиксируем баланс на начало работы сессии робота
        if k == 0:

            start_balance_units, start_shares = account_manager.get_current_balance()
            k += 1

        profit = 0 #Установим счетчик прибыли сессии в деньгах
        profit_shares = 0 #Установим счетчик роста портфеля


        real_market_data_from = start_datetime() #Зафиксируем время начало работы робота
        #Рассчитаем время после, которого у робота должно быть достаточно данных для работы стратегии
        real_market_data_start = start_datetime() + timedelta(minutes=max(std_period,long_ma)) 
        
        logger.info(f"Интервал: Дата начала получения свечей = {real_market_data_from}, Дата начала торговли (проверки сигналов) = {real_market_data_start}")
        logger.info(f"Начальный баланс =  {start_balance_units}") 
        logger.info(f"Начальный баланс акций=  {start_shares}")      
        
        
        response = {} #Структура для возврата информации телеграмм боту
        
        for marketdata in market_data_stream:
            print(marketdata) #Создает ощущение матрицы в терминале
            market_data_stream.info.subscribe([InfoInstrument(figi)])  #Подписываемся на получение информации о акциях ВТБ

                        
            market_order_available_flag = client.market_data.get_trading_status(figi = default_stock['figi']).market_order_available_flag
            if market_order_available_flag: #Торговля доступна  
                moving_average_strategy_trader.trade()

                
                balance, shares = account_manager.get_current_balance() 
                profit = float(balance - start_balance_units + shares - start_shares)
                profit_shares =  float(shares - start_shares)      
        

                response = {
                   'status': "Working",
                   'profit': profit,
                   'profit_shares': profit_shares,
                   'balance': balance,
                   'shares': shares
                }
                yield response  #Вернем телеграмм боту информцию о текущей работе робота
                time.sleep(60) #Уснем на 60 секунд. Свечи то, минутные ))
            
                
            else:
               market_data_stream.stop()
               
               client.cancel_all_orders(account_id=account_id) #Закроем все ордера

               balance, shares = account_manager.get_current_balance() 
               profit = float(balance - start_balance_units + shares - start_shares)
               profit_shares =  float(shares - start_shares)    

               response = {
                   'status': "Торги сейчас не ведуться",
                   'profit': profit,
                   'profit_shares': profit_shares,
                   'balance': balance,
                   'shares': shares
               }              
               yield response
            



        #if direct_action == "stop":
        #    logger.info(f"Прибыль от сессии робота в кэше =  {profit}")
        #    logger.info(f"Прибыль от сессии робота в акциях =  {profit_shares}")
        #    logger.info(f"Дата окончания тестовой торговли = {start_datetime()}")
           
            

if __name__ == "__main__":
    main()



