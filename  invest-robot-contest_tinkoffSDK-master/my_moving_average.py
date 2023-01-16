import sys
import os
from urllib import response

path = os.getcwd()
repo_folder = os.path.dirname(os.path.dirname(path))
sys.path.append(repo_folder)
#!set PATH=%PATH%;%APPDATA%\Python\Scripts
#os.chdir(os.path.dirname(os.path.dirname(path)))

import logging
import operator

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

import my_account_manager
import my_trader
import my_strategy

#Все даты учитываются по всемирному времени
def start_datetime() -> datetime:
    return datetime(year=2022, month=5, day=23, hour=7, tzinfo=timezone.utc)

def main(start_balance_units = 100000, long_ma_min = 30, long_ma_max = 30, short_ma_min = 3, short_ma_max = 3, std_period_min = 22,  std_period_max = 22) -> dict:
    
    print("Start")
   
    # sandbox token
    token = os.environ["SANDBOX_TOKEN"]

   

    d_long_ma = [] #Диапазон настроек long_ma
    for i in range(long_ma_min, long_ma_max+1):
        d_long_ma.append(i)

    d_short_ma = []
    for i in range(short_ma_min, short_ma_max+1):
        d_short_ma.append(i)

    d_std_period = []
    for i in range(std_period_min, std_period_max+1):
        d_std_period.append(i)

    d_candle_interval = []
    d_candle_interval.append(CandleInterval.CANDLE_INTERVAL_1_MIN)
  #  d_candle_interval.append(CandleInterval.CANDLE_INTERVAL_5_MIN)
  #  d_candle_interval.append(CandleInterval.CANDLE_INTERVAL_15_MIN)
  #  d_candle_interval.append(CandleInterval.CANDLE_INTERVAL_HOUR)

    long_ma = 15
    short_ma = 3
    std_period = 30
    timaframe = CandleInterval.CANDLE_INTERVAL_1_MIN
    n, m, s, tf = long_ma, short_ma, std_period, timaframe
    period = 1  # сюда добавить переход от tf к числу или отрекдактировать код снизу

    stocks = {
        #"AAPL": {"figi": "BBG000B9XRY4"},
        #"GAZP": {"figi": "BBG004730RP0"}
        "VTB": {"figi": "BBG004730ZJ9"}  
        #"MSFT": {"figi": "BBG000BPH459"},
        # "GOOG":{"figi":"BBG009S3NB30"}, гугл не работает
        #"AMZN": {"figi": "BBG000BVPV84"},
        #"TSLA": {"figi": "BBG000N9MNX3"},
        # "NGK2": {"figi": os.environ["FIGI"]}
    }

    default_stock = {"figi": "BBG004730ZJ9"}  

    settings_data = {} # в этот словарь будут записываться сгенерированные настройки.
    settings_data['default'] = {
        "stock":  default_stock,
        'long_ma' : long_ma, 
        'short_ma' : short_ma,
        'std_period' : std_period,
        'tf' : timaframe,
        'period' : period
    }

    k = 0
    settings_name = "set" + str(k) #Переменная будет хранить ключи настроек

    #Сгенерируем все наборы настроек:
    for ci in d_candle_interval:
        for dlm in d_long_ma:
            for dsm in d_short_ma:
                for dsp in d_std_period:
                    settings_data[settings_name] = {
                        "stock":  default_stock,
                        'long_ma' : dlm, 
                        'short_ma' : dsm,
                        'std_period' : dsp,
                        'tf' : ci,
                        'period' : period  # пока константа
                    }
                    k += 1
                    settings_name = "set" + str(k)




    

    # тут надо проставлять сдвиг даты в зависимости от выбранного тф
    # что-то вроде CandleInterval.CANDLE_INTERVAL_1_MIN.seconds * (m+n) для real_market_data_test_from
    real_market_data_test_from = start_datetime()  # с какой даты начинают считаться индикаторы
    #real_market_data_test_start = start_datetime() + timedelta(minutes=(n + m) * 20)  # с какой даты начинает работать стратегия
    real_market_data_test_start = start_datetime() + timedelta(hours=1)
    #real_market_data_test_end = start_datetime() + timedelta(days=1)
    real_market_data_test_end = start_datetime() + timedelta(hours=8) # когда все заканчивается

    takts_count = 420 #Количество тактов робота в минутах, если интервал свеч Минута

    start_balance = MoneyValue(currency="rub", units = start_balance_units, nano=000000000)
    
    #Начнем логирование здесь:
    file_name = "Log_mov_aver__shortMA_%s, longMA_%s, stdP_%s,tf_%s.log" %(short_ma,long_ma, std_period,timaframe) 
    logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO, filename = file_name)
    logger = logging.getLogger(__name__)

    logger.info("Параметры теста _shortMA_%s, longMA_%s, stdP_%s,tf_%s.log" %(short_ma,long_ma, std_period,timaframe))
    logger.info(f"Интервал: Дата начала получения свечей = {real_market_data_test_from}, Дата начала торговли (проверки сигналов) = {real_market_data_test_start}, Дата окончания тестовой торговли = {real_market_data_test_end}")
    logger.info(f"Начальный баланс =  {start_balance}")


    balances = {}
    results = []
    maxprofit = 0
    best_settings = "none"
    #results["none"] = {'profit': "none"} 

    for set in settings_data:

        figi = ShareId(settings_data[set]['stock']['figi'])

        logger.info(f'Инструмент =  {figi}')

        balance = MoneyValue(currency="rub", units = start_balance_units, nano=000000000)

        

        #account_id = AccountId("1337007228")
        account_id = os.environ["INVEST_ACCOUNT_ID"]
        settings = MovingAverageStrategySettings(
            share_id=figi,  # figi конкретной ценной бумаги
            account_id=account_id,  # неважно для sandbox
            max_transaction_price=Decimal(
                100000
            ),  # максимальный объем сделки - зависит от размера портфеля. сейчас фиксировано
            candle_interval=settings_data[set]['tf'],  # тф - таймфрейм
            long_period=timedelta(minutes=settings_data[set]['long_ma'] * settings_data[set]['period']),  # длинная скользяшка
            short_period=timedelta(minutes=settings_data[set]['short_ma'] * settings_data[set]['period']),  # короткая скользяшка
            std_period=timedelta(minutes=settings_data[set]['std_period']  * settings_data[set]['period']),  # количество периодов для стд
        )

        with MockedClient(
            token=token,
            settings=settings,
            real_market_data_test_from=real_market_data_test_from,
            real_market_data_test_start=real_market_data_test_start,
            real_market_data_test_end=real_market_data_test_end,
            balance=balance,
        ) as mocked_services:
            account_manager = my_account_manager.AccountManager(
                services=mocked_services, strategy_settings=settings
            )
            state = MovingAverageStrategyState()
            strategy = my_strategy.MovingAverageStrategy(
                settings=settings,
                account_manager=account_manager,
                state=state,
            )
            supervisor = MovingAverageStrategySupervisor()
            signal_executor = MovingAverageSignalExecutor(
                services=mocked_services,
                state=state,
                settings=settings,
            )
            moving_average_strategy_trader = my_trader.MovingAverageStrategyTrader(
                strategy=strategy,
                settings=settings,
                services=mocked_services,
                state=state,
                signal_executor=signal_executor,
                account_manager=account_manager,
                supervisor=supervisor,
            )
            
            
                    
            plotter = MovingAverageStrategyPlotter(settings=settings)
            

            initial_balance = account_manager.get_current_balance()
            
            for i in range(takts_count):
                logger.info("Trade %s", i)
                moving_average_strategy_trader.trade()

            balance, shares = account_manager.get_current_balance()
            
            balances[set] = {'cash': balance, 'shares': shares}

            profit = balance - start_balance_units + shares

            results.append({"settings": settings_data[set], "balance": balances[set], "profit": profit})

            if profit > maxprofit:
                maxprofit = profit
                best_settings = set

            logger.info(f"РЕЗУЛЬТАТЫ:")
            logger.info(f"Конечный баланс =  {balance}")
            logger.info(f"Инструмент =  {default_stock}")
            logger.info("Параметры теста _shortMA_%s, longMA_%s, stdP_%s,tf_%s.log" %(settings_data[set]['short_ma'],settings_data[set]['long_ma'] , settings_data[set]['std_period'],settings_data[set]['tf']))
            logger.info(f"Интервал: Дата начала получения свечей = {real_market_data_test_from}, Дата начала торговли (проверки сигналов) = {real_market_data_test_start}, Дата окончания тестовой торговли = {real_market_data_test_end}")
            logger.info(f"Начальный баланс =  {start_balance_units}")
            
            if balance + shares - start_balance_units > 0:
                logger.info(f"Результат = Успешная торговля! Прибыль =  {balance - start_balance_units}")
                #result = f"Результат = Успешная торговля! Прибыль =  {balance.units - start_balance.units}"
            #elif state.long_open:
            #    logger.info(f"Есть открытые позиции. Количество открытых позиций {state.position}")
            #    result = f"Есть открытые позиции. Количество открытых позиций {state.position}"
            elif  balance.units + shares.units - start_balance_units == 0:
                logger.info(f"Результат = Нейтральный! Прибыль =  {balance - start_balance_units}")
            else:
                logger.info(f"Результат = Убыток! Убыток =  {balance - start_balance_units}")
            

    #best_stock = max(balances, key=balances.get)
    #best_stock = max(results, key=results.get)
    


   # events = supervisor.get_events()
  #  plotter.plot(events)

    #current_balance = account_manager.get_current_balance()
    # assert initial_balance != current_balance
    # logger.info("Initial balance %s", initial_balance)
    # logger.info("Current balance %s", current_balance)
    
    


    sorted_results = sorted(results, key = operator.itemgetter('profit'),reverse=True)

    
    return sorted_results
    

if __name__ == "__main__":
    main()