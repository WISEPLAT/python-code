from datetime import datetime, timedelta

from tinkoff.invest import CandleInterval, Quotation, AccessLevel, AccountStatus, AccountType


def Qt(obj: Quotation) -> float:
    return obj.units + obj.nano / 1e9


def TradeSession(client, exchange):
    '''
    Проверяем можно ли сейчас торговать или сессия закрыта
    торговлю начинаем через 5 минут после открытия торгов
    и заканчиваем за 15 минут до окончания
    '''
    tms = client.instruments.trading_schedules(from_=datetime.utcnow(), to=datetime.utcnow())
    for i in tms.exchanges:
        if i.exchange == exchange:
            if i.days[0].is_trading_day:
                if i.days[0].start_time.timestamp() > datetime.utcnow().timestamp():
                    start_time = i.days[0].start_time + timedelta(minutes=5)
                    end_time = i.days[0].end_time - timedelta(minutes=15)
                    return True, start_time, end_time
    return False,


def GetHistoryData(client, figi, from_data, to_date, interval):
    '''
    получаем историю по выбранному интсрументу
    '''
    candles = client.market_data.get_candles(figi=figi, from_=from_data, to=to_date, interval=interval)

    data = []
    for i in candles.candles:
        data.append((Qt(i.open), Qt(i.high), Qt(i.low), Qt(i.close), i.volume, str(i.time), i.is_complete))

    return data


def SynchronizationTwoArray(smb_1, smb_2):
    smb_1_index = 0
    smb_2_index = 0
    len_common = min(len(smb_1), len(smb_2))

    out_1 = []
    out_2 = []

    while True:
        # ('open', 'high', 'low', 'close', 'volume', 'time', 'bar complete')
        dt1 = smb_1[smb_1_index][5]
        dt2 = smb_2[smb_2_index][5]

        if dt1 > dt2:
            smb_2_index += 1
            continue

        if dt1 < dt2:
            smb_1_index += 1
            continue

        out_1.append(smb_1[smb_1_index])
        out_2.append(smb_2[smb_2_index])

        smb_1_index += 1
        smb_2_index += 1

        if smb_1_index >= len_common or smb_2_index >= len_common:
            break

    return out_1, out_2


def AbsoluteToRelative(smb, start_price):
    '''
    оставляем только отношение к цене открытия. Остальные данные отбрасываем
    цена открытия плавающая, чтобы была возможность её менять при закрытии сделки внутри дня
    '''
    data = list(map(lambda i: float(i[3] / start_price - 1) * 100, smb))
    data.insert(0, 0)
    return data


def CalcMinDelta():
    '''
    Рассчитываем минимально необходимое расхождение между активами необхадимое для входа
    другими словами складываем все комиссионные издержки и переводимв относительную шкалу
    '''
    return abs(0.2)


def FigiToTicker(figi) -> str:
    '''
    получаем тикер по фиги
    '''
    return ''


def FindTwoInstruments():
    '''
    Функция поиска необходимой пары инструментов
    Можно использовать коинтеграцию.
    Если инструменты схожи или из одного сектора экономики то можно использовать корреляцию
    Также можно использовать один инструмент но с разных бирж или секиий одной биржи
    к акция + её адр
    или спот+фьюч
    '''
    SRM2 = 'FUTSBRF06220'
    VBM2 = 'FUTVTBR06220'
    return SRM2, VBM2


def FindOpenDeals(client, account_id):
    '''
    Ищем открытые сделки
    '''
    acc = client.sandbox.get_sandbox_positions(account_id=account_id)
    return acc.futures


def OpenDeal(client, account_id, figi, lots, direction, order_type, order_id, sandbox):
    '''
    Отправляем ордер.Пока работаем только с маркетами
    '''
    if sandbox:
        r = client.sandbox.post_sandbox_order(figi=figi, quantity=lots, account_id=account_id, direction=direction,
                                              order_type=order_type, order_id=order_id)
    else:
        r = client.orders.post_order(figi=figi, quantity=lots, account_id=account_id, direction=direction,
                                     order_type=order_type, order_id=order_id)
    return r


def CloseAccountSandbox(client, account_id):
    try:
        client.sandbox.close_sandbox_account(account_id=account_id)
    except:
        pass


def GetAccountSandbox(client):
    # в песочнице берём первый акк
    acc = client.sandbox.get_sandbox_accounts()
    if acc.accounts == []:
        acc = client.sandbox.open_sandbox_account()
        return acc.account_id
    return acc.accounts[0].id


def GetBalance(client, sandbox, account_id):
    if sandbox:
        acc = client.sandbox.get_sandbox_portfolio(account_id=account_id)
        return acc.total_amount_currencies
