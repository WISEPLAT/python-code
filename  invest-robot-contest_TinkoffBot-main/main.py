from time import sleep

from tinkoff.invest import Client, OrderDirection, OrderType, MoneyValue

from lib.func import *
from settings import Token, AccountNum

TOKEN = Token.broker_full
ACCOUNT_ID = AccountNum.broker
APP_NAME = 'Desead'
SANDBOX = True
LOT_1 = 1
LOT_2 = 1
SAVE_DATA_FILE = False
SAVE_FILE_NAME = 'all_data.csv'


def main():
    with Client(token=TOKEN, app_name=APP_NAME) as client:
        # CloseAccountSandbox(client, account_id='3dfdcd62-4f5e-49c6-990c-c88e1a1de356')

        #   ================   Получаем account_id  ================
        #   ========================================================
        if SANDBOX:
            account_id = GetAccountSandbox(client)
            if GetBalance(client, SANDBOX, account_id).units == 0:  # если баланс = 0 закинем туда 1 млн
                client.sandbox.sandbox_pay_in(account_id=account_id,
                                              amount=MoneyValue(currency='rub', units=1000000, nano=0))
        else:
            account_id = ACCOUNT_ID
        print('account_id:', account_id)

        #   ================   Ищем необходимые для торговли пары инструментов  ==========
        #   ==============================================================================
        smb_1_figi, smb_2_figi = FindTwoInstruments()
        print('Используемый инструмент 1:', smb_1_figi)
        print('Используемый инструмент 2:', smb_2_figi)

        #   ================   Проверяем торговые сессии  ==========
        #   ========================================================
        # trade_time=(True, start_time_trade, end_time_trade)
        trade_time = TradeSession(client, 'FORTS')

        open_figi = None
        lot = 0
        direction = None

        while True:
            #   ================   Получаем исторические данные  ===========
            #   ============================================================
            smb_1_data = GetHistoryData(client, smb_1_figi, datetime.utcnow() - timedelta(minutes=24 * 60),
                                        datetime.utcnow(), CandleInterval.CANDLE_INTERVAL_1_MIN)
            smb_2_data = GetHistoryData(client, smb_2_figi, datetime.utcnow() - timedelta(minutes=24 * 60),
                                        datetime.utcnow(), CandleInterval.CANDLE_INTERVAL_1_MIN)
            print('Всего получено свечей по инструменту 1:', len(smb_1_data))
            print('Всего получено свечей по инструменту 2:', len(smb_2_data))

            #   ================   Синхронизируем исторические данныи  ===========
            #   ==================================================================
            smb_1_data, smb_2_data = SynchronizationTwoArray(smb_1_data, smb_2_data)
            start_index = 0
            smb_1_start_price = float(smb_1_data[start_index][0])
            smb_2_start_price = float(smb_2_data[start_index][0])
            print('Свечей после синхронизации по инструменту 1:', len(smb_1_data))
            print('Свечей после синхронизации по инструменту 2:', len(smb_2_data))
            print('Стартовая цена по инструменту 1:', smb_1_start_price)
            print('Стартовая цена по инструменту 2:', smb_2_start_price)

            #   ================   Переводим в относительную шкалу  ==============
            #   ==================================================================
            smb_1_relative = AbsoluteToRelative(smb_1_data, smb_1_start_price)
            smb_2_relative = AbsoluteToRelative(smb_2_data, smb_2_start_price)

            #   ================   Скинем данные в файл при необходимости  ==============
            #   =========================================================================
            if SAVE_DATA_FILE:
                with open(SAVE_FILE_NAME, mode='w') as fl:
                    fl.write('time;;open_1;high_1;low_1;close_1;;open_2;high_2;low_2;close_2;;0;0;delta\n')
                    for k, v in enumerate(smb_1_data):
                        fl.write(str(smb_1_data[k][5]) + ';;' +
                                 str(smb_1_data[k][0]) + ';' +
                                 str(smb_1_data[k][1]) + ';' +
                                 str(smb_1_data[k][2]) + ';' +
                                 str(smb_1_data[k][3]) + ';;' +
                                 str(smb_2_data[k][0]) + ';' +
                                 str(smb_2_data[k][1]) + ';' +
                                 str(smb_2_data[k][2]) + ';' +
                                 str(smb_2_data[k][3]) + ';;' +
                                 str(smb_1_relative[k + 1]) + ';' +
                                 str(smb_2_relative[k + 1]) + ';' +
                                 str(smb_1_relative[k + 1] - smb_2_relative[k + 1]) +
                                 '\n')

            #   ================   Считаем текущую дельту и если она привышает пороговое значение то входим в сделку
            #   ====================================================================================================
            delta_1 = smb_1_relative[-1]
            delta_2 = smb_2_relative[-1]
            delta = round(delta_1 - delta_2, 3)
            print('Текущее расхождение: ', delta)

            # Открываем новую сделку только если нет другой открытой сделки по этой паре инструментов
            order_id = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if FindOpenDeals(client, account_id) == []:
                if delta_1 * delta_2 > 0:  # если оба инструмента движутся в одном направлении
                    if abs(delta) >= CalcMinDelta():
                        if delta_1 > 0:  # если движемся вверх
                            if delta > 0:  # значит покупаем инструмент 2
                                open_figi = smb_2_figi
                                lot = LOT_2
                                direction = OrderDirection.ORDER_DIRECTION_BUY
                            if delta < 0:  # значит покупаем инструмент 1
                                open_figi = smb_1_figi
                                lot = LOT_1
                                direction = OrderDirection.ORDER_DIRECTION_BUY
                        if delta_1 < 0:  # если движемся вниз
                            if delta > 0:  # значит продаём инструмент 1
                                open_figi = smb_1_figi
                                lot = LOT_1
                                direction = OrderDirection.ORDER_DIRECTION_SELL
                            if delta < 0:  # значит продаём инструмент 2
                                open_figi = smb_2_figi
                                lot = LOT_2
                                direction = OrderDirection.ORDER_DIRECTION_SELL
            else:  # проверяем не пора ли закрыть сделки
                if trade_time[0]:
                    if datetime.utcnow().timestamp() >= trade_time[2]:
                        if direction == OrderDirection.ORDER_DIRECTION_SELL:
                            direction = OrderDirection.ORDER_DIRECTION_BUY
                        else:
                            direction = OrderDirection.ORDER_DIRECTION_SELL

            if lot > 0:
                r = OpenDeal(client, account_id, open_figi, lot, direction, OrderType.ORDER_TYPE_MARKET, order_id,
                             SANDBOX)

            sleep(60)


if __name__ == '__main__':
    main()
