import logging
import tinkoff.invest as ti
from datetime import datetime
from functions import get_shares_figi, get_time_series, create_df_from_stream, recalculate_time_series,\
    get_sandbox_account_id, convert_price, get_shares_lot_size, INSTRUMENT_TICKER


TOKEN = 'TOKEN'
INITIAL_DIRECTION = 1  # Направление сделки: 0 - покупка, 1 - продажа


def test_hypothesis():
    with ti.Client(TOKEN) as client:
        sharefigi = get_shares_figi(client, INSTRUMENT_TICKER)
        sharecandles = get_time_series(client, sharefigi)
        # Проверка гипотезы на последних 500 записях
        money = 10000  # Первоначальная баланс счета
        akcii = 0  # Направление сделки: 0 - покупка, 1 - продажа
        n = sharecandles.shape[0] - 500
        lot = get_shares_lot_size(client, INSTRUMENT_TICKER)
        for i in range(500):
            k = sharecandles.loc[i + n, '%K']
            d = sharecandles.loc[i + n, '%D']
            price = sharecandles.loc[i + n, 'close']
            t = sharecandles.loc[i + n, 'time']
            if k < d < 20 and akcii == 0:
                print(t, 'Покупка акции', INSTRUMENT_TICKER, 'по цене', price)
                akcii = 1
                money = money - price * lot
            if k > d > 80 and akcii == 1:
                print(t, 'Продажа акции', INSTRUMENT_TICKER, 'по цене', price)
                akcii = 0
                money = money + price * lot
        print('Баланс счета', money)
        print('Количество акций на счете', akcii)


def start():
    logging.basicConfig(filename='tinkoff_invest_bot_sandbox.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')
    with ti.Client(TOKEN, app_name='Loginov-Mikhail_TinkoffInvestBot') as client:
        sandbox_account_id = get_sandbox_account_id(client)
        sharefigi = get_shares_figi(client, INSTRUMENT_TICKER)
        sharecandles = get_time_series(client, sharefigi)
        # Включение подписки на свечи указанного тикера
        market_data_stream = client.create_market_data_stream()
        market_data_stream.candles.subscribe(
            [
                ti.CandleInstrument(
                    figi=sharefigi,
                    interval=ti.SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
                )
            ]
        )
        akcii = INITIAL_DIRECTION
        oi = ''  # order_id - необходим для проверки исполнения выставленной заявки
        for marketdata in market_data_stream:
            print(marketdata)
            if marketdata.subscribe_candles_response is not None:
                print(marketdata.subscribe_candles_response.tracking_id)
                logging.info('Включена подписка на данные для инструмента ' + INSTRUMENT_TICKER + ' c tracking_id=' +
                             marketdata.subscribe_candles_response.tracking_id)
            if marketdata.candle is not None:
                # TODO: Добавить проверку на завершение периода свечи
                tempdf = create_df_from_stream(marketdata.candle)
                sharecandles = recalculate_time_series(sharecandles, tempdf)
                # print(sharecandles.tail())
                j = sharecandles.index[-1]
                k = sharecandles.loc[j, '%K']
                d = sharecandles.loc[j, '%D']
                price = sharecandles.loc[j, 'close']
                t = sharecandles.loc[j, 'time']
                print(t, price)
                logging.info('Цена закрытия ' + str(price))
                if oi != '':
                    r = client.sandbox.get_sandbox_order_state(account_id=sandbox_account_id, order_id=oi)
                    if r.lots_executed > 0:
                        logging.info('Заявка ' + oi + ' исполнена по цене ' +
                                     str(convert_price(r.executed_order_price)) + ' в ' +
                                     r.order_date.strftime('%Y-%m-%d %H:%M:%S'))
                        oi = ''
                if k < d < 20 and akcii == 0 and oi == '':
                    print(t, k, d, price, 'Купить')
                    akcii = 1
                    datestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    r = client.sandbox.post_sandbox_order(figi=sharefigi, quantity=1, account_id=sandbox_account_id,
                                                          order_id='Loginov-Mikhail_TinkoffInvestBot_'+datestr,
                                                          direction=ti.OrderDirection.ORDER_DIRECTION_BUY,
                                                          order_type=ti.OrderType.ORDER_TYPE_LIMIT,
                                                          price=marketdata.candle.close)
                    print(r)
                    oi = r.order_id
                    logging.info('Выставлена заявка ' + oi + ' на покупку одного лота ' + INSTRUMENT_TICKER +
                                 ' по цене ' + str(convert_price(marketdata.candle.close)))
                if k > d > 80 and akcii == 1 and oi == '':
                    print(t, k, d, price, 'Продать')
                    akcii = 0
                    datestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    r = client.sandbox.post_sandbox_order(figi=sharefigi, quantity=1, account_id=sandbox_account_id,
                                                          order_id='Loginov-Mikhail_TinkoffInvestBot_' + datestr,
                                                          direction=ti.OrderDirection.ORDER_DIRECTION_SELL,
                                                          order_type=ti.OrderType.ORDER_TYPE_LIMIT,
                                                          price=marketdata.candle.close)
                    print(r)
                    oi = r.order_id
                    logging.info('Выставлена заявка ' + oi + ' на продажу одного лота ' + INSTRUMENT_TICKER +
                                 ' по цене ' + str(convert_price(marketdata.candle.close)))


if __name__ == '__main__':
    test_hypothesis()
    start()
