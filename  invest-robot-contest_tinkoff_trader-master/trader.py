## 19.05.2020   Учимся покупать несколько акций #Buy_several_stocks
## 21.05.2020   Комиссию из баланса вычитаем и при покупке и при продаже #Commission_during_buying
## 11.08.2020   Засыпать, если Too Many Requests  #TooManyRequests_Sleep
## 21.12.2020   seconds->total_seconds: if (datetime.now()-r['time']).total_seconds() > 60*60*24: # Expires after 24 hours
## 03.09.2021   Skip 'min_price_increment': None #Skip 'min_price_increment': None
##              #SellStocksWithLoss
##              Mind spread #MindSpread

from openapi_client import openapi
from datetime import datetime, timedelta
from pytz import timezone
import time
import os


def check_find_curve_c(figi, v_days, period, price, descent_perc = 2, advance_perc = 0.5, times = 1):
    time_to = datetime.now()
    time_from = time_to + timedelta(days=-1 * v_days)    

    try:
        response = client.market.market_candles_get(figi,time_from.strftime(g_fmt),time_to.strftime(g_fmt),period)
    except Exception as err:
        output(figi + ' ' + str(err))
        log(figi + ' market_candles_get: ' + str(err), 'error_log.txt')
        return None

        
    candles = getattr(getattr(response, 'payload'), 'candles')
    
    res = {}
    res['0 current_value'] = price
    t = 1
    stage = 'Advance ' + str(t)
    for i in (sorted(candles, key=lambda d: getattr(d, 'time'), reverse=True)):
        if stage == 'Advance ' + str(t) and t > 1 and getattr(i, 'c') > res[str(t-1) + '_high_value']:
            res[str(t-1) + '_high_value'] = getattr(i, 'c')
            res[str(t-1) + '_high_time'] = getattr(i, 'time')
        elif stage == 'Advance ' + str(t) and getattr(i, 'c') < res['0 current_value'] / 100 * (100 - advance_perc):
            res[str(t) + ' low_value'] = getattr(i, 'c')
            res[str(t) + ' low_time'] = getattr(i, 'time')
            stage = 'Descent ' + str(t)
        elif stage == 'Descent ' + str(t) and getattr(i, 'c') < res[str(t) + ' low_value']:
            res[str(t) + ' low_value'] = getattr(i, 'c')
            res[str(t) + ' low_time'] = getattr(i, 'time')
        elif stage == 'Descent ' + str(t) and getattr(i, 'c') > res['0 current_value'] / 100 * (100 + descent_perc) and t < times:
            res[str(t) + '_high_value'] = getattr(i, 'c')
            res[str(t) + '_high_time'] = getattr(i, 'time')
            t += 1
            stage = 'Advance ' + str(t)
        elif stage == 'Descent ' + str(t) and getattr(i, 'c') > res['0 current_value'] / 100 * (100 + descent_perc) and t == times:
            res[str(t) + '_high_value'] = getattr(i, 'c')
            res[str(t) + '_high_time'] = getattr(i, 'time')
            stage = 'Found'
        elif stage == 'Found ' + str(t) and getattr(i, 'c') > res[str(t) + '_high_value'] and t == times:
            res[str(t) + '_high_value'] = getattr(i, 'c')
            res[str(t) + '_high_time'] = getattr(i, 'time')
     
    if stage == 'Found':
        return res

def check_find_curve(figi, v_days, period, price, descent_perc = 2, advance_perc = 0.5, times = 1):
    time_to = datetime.now()
    time_from = time_to + timedelta(days=-1 * v_days)    

    try:
        response = client.market.market_candles_get(figi,time_from.strftime(g_fmt),time_to.strftime(g_fmt),period)
    except Exception as err:
        output(figi + ' ' + str(err))
        log(figi + ' market_candles_get: ' + str(err), 'error_log.txt')
        return None

        
    candles = getattr(getattr(response, 'payload'), 'candles')
    
    res = {}
    res['0 current_value'] = price
    t = 1
    stage = 'Advance ' + str(t)
    for i in (sorted(candles, key=lambda d: getattr(d, 'time'), reverse=True)):
        if stage == 'Advance ' + str(t) and t > 1 and getattr(i, 'h') > res[str(t-1) + '_high_value']:
            res[str(t-1) + '_high_value'] = getattr(i, 'h')
            res[str(t-1) + '_high_time'] = getattr(i, 'time')
        # Several conditions may be true
        if stage == 'Advance ' + str(t) and getattr(i, 'l') < res['0 current_value'] / 100 * (100 - advance_perc):
            res[str(t) + ' low_value'] = getattr(i, 'l')
            res[str(t) + ' low_time'] = getattr(i, 'time')
            stage = 'Descent ' + str(t)
        elif stage == 'Descent ' + str(t) and getattr(i, 'l') < res[str(t) + ' low_value']:
            res[str(t) + ' low_value'] = getattr(i, 'l')
            res[str(t) + ' low_time'] = getattr(i, 'time')
        # Several conditions may be true    
        if stage == 'Descent ' + str(t) and getattr(i, 'h') > res['0 current_value'] / 100 * (100 + descent_perc) and t < times:
            res[str(t) + '_high_value'] = getattr(i, 'h')
            res[str(t) + '_high_time'] = getattr(i, 'time')
            t += 1
            stage = 'Advance ' + str(t)
        elif stage == 'Descent ' + str(t) and getattr(i, 'h') > res['0 current_value'] / 100 * (100 + descent_perc) and t == times:
            res[str(t) + '_high_value'] = getattr(i, 'h')
            res[str(t) + '_high_time'] = getattr(i, 'time')
            stage = 'Found'
        elif stage == 'Found ' + str(t) and getattr(i, 'h') > res[str(t) + '_high_value'] and t == times:
            res[str(t) + '_high_value'] = getattr(i, 'h')
            res[str(t) + '_high_time'] = getattr(i, 'time')
     
    if stage == 'Found':
        return res

def check_level(figi, start_period_days, end_period_days, period, high_level, p_high_level_qty, low_level, p_low_level_qty):
    time_to = datetime.now() + timedelta(days=-1 * end_period_days)
    time_from = datetime.now() + timedelta(days=-1 * start_period_days)
    v_high_level_qty = 0
    v_low_level_qty = 0

    try:
        response = client.market.market_candles_get(figi,time_from.strftime(g_fmt),time_to.strftime(g_fmt),period)
    except Exception as err:
        output(figi + ' ' + str(err))
        log(figi + ' market_candles_get: ' + str(err), 'error_log.txt')
        return None

    candles = getattr(getattr(response, 'payload'), 'candles')
    
    res = {}
    res['1 start_time'] = time_from
    res['2 end_time'] = time_to
    res['3 period'] = period
    res['4 high_level'] = high_level
    res['5 low_level'] = low_level
    res['6 high_level_qty'] = 0
    res['7 low_level_qty'] = 0
    t = 1
    for i in (sorted(candles, key=lambda d: getattr(d, 'time'), reverse=True)):
        if getattr(i, 'h') >= high_level:
            res['6 high_level_qty'] = res['6 high_level_qty'] + 1
        if getattr(i, 'l') <= low_level:
            res['7 low_level_qty'] = res['7 low_level_qty'] + 1
            
    if res['6 high_level_qty'] >= p_high_level_qty and res['7 low_level_qty'] >= p_low_level_qty:
        return res

def should_i_stop():
    with open('delete_to_stop.txt', 'r') as stp_file:
        None

def log(message, file_name='log.txt'):
    
    if file_name =='log.txt' or file_name =='error_log.txt':
        try:
            trial_str = g_trial + '  '
        except NameError:
            trial_str = ''
    else:
        trial_str = ''

    print(trial_str + str(message))
    
    if str(message).find('Reason: Too Many Requests') > 0 and file_name =='error_log.txt': #TooManyRequests_Sleep
        print('Sleep')
        time.sleep(5)
    else:
        f = open(file_name, 'a')
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ '  ' + trial_str + str(message) + '\n')
        f.close()
        

def output(message):
    print(g_trial + ' ' + str(message))

def buy(ticker, figi, lot_qty, lot, currency, price):
    v_lot_qty = int(lot_qty)
    with open(g_trial + '/bought.txt', 'a') as g:
            g.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                   ' ' + str(ticker).ljust(12, ' ') +
                   ' ' + str(figi).ljust(12, ' ') +
                   ' ' + str(v_lot_qty).ljust(5, ' ') +
                   ' ' + str(lot).ljust(7, ' ') +
                   ' ' + str(currency).ljust(4, ' ') +
                   ' ' + str(price) + '\n')
    return price*v_lot_qty*lot

def get_bought():
    b = []
    try:
        with open(g_trial + '/bought.txt', 'r') as f:
            for item in f:
                b.append({'time':datetime(int(item[0:4]), int(item[5:7]), int(item[8:10]), int(item[11:13]), int(item[14:16]), int(item[17:19])),
                          'ticker':item[20:33].rstrip(),
                          'figi':item[33:46].rstrip(),
                          'lot_qty':int(float(item[46:52])),
                          'lot':int(item[52:60]),
                          'currency':item[60:63],
                          'price':float(item[65:].rstrip())
                          })
    except FileNotFoundError:
        return b
    return b

def get_comission(p_amount):
    v_amount = round(p_amount * float(g_trial_params['COMMISSION']), 2)
    if v_amount < 0.01:
        v_amount = 0.01
    return v_amount

def sell(ticker, lot_qty, price):
    part_qty = 0
    bb = get_bought()
    with open(g_trial + '/bought.txt', 'w') as f:
        for b in (bb):
            if b['ticker'] == ticker and b['lot_qty'] <= lot_qty-part_qty:
                part_qty = part_qty+b['lot_qty']
                with open(g_trial + '/sold.txt', 'a') as sf:
                    sf.write(b['time'].strftime('%Y-%m-%d %H:%M:%S') +
                            '  ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                            ' ' + str(b['ticker']).ljust(12, ' ') +
                            ' ' + str(b['figi']).ljust(12, ' ') +
                            ' ' + str(b['lot_qty']).ljust(5, ' ') +
                            ' ' + str(b['lot']).ljust(7, ' ') +
                            ' ' + str(b['currency']).ljust(4, ' ') +
                            ' ' + str(b['price']).ljust(10, ' ') +
                            ' ' + str(price).ljust(10, ' ') +
                            ' ' + str(round(price*b['lot_qty']*b['lot'] - get_comission(price*b['lot_qty']*b['lot']) - b['price']*b['lot_qty']*b['lot'] - get_comission(b['price']*b['lot_qty']*b['lot']),2)) # Profit
                                + '\n')
            elif b['ticker'] == ticker:
                with open(g_trial + '/sold.txt', 'a') as sf:
                    if lot_qty-part_qty != 0:
                        sf.write(b['time'].strftime('%Y-%m-%d %H:%M:%S') +
                                '  ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                                ' ' + str(b['ticker']).ljust(12, ' ') +
                                ' ' + str(b['figi']).ljust(12, ' ') +
                                ' ' + str(lot_qty-part_qty).ljust(5, ' ') +
                                ' ' + str(b['lot']).ljust(7, ' ') +
                                ' ' + str(b['currency']).ljust(4, ' ') +
                                ' ' + str(b['price']).ljust(10, ' ') +
                                ' ' + str(price).ljust(10, ' ') +
                                ' ' + str(round(price*(lot_qty-part_qty)*b['lot'] - get_comission(price*(lot_qty-part_qty)*b['lot']) - b['price']*(lot_qty-part_qty)*b['lot'] - get_comission(b['price']*(lot_qty-part_qty)*b['lot']) ,2))  # Profit
                                    + '\n')

                    f.write(b['time'].strftime('%Y-%m-%d %H:%M:%S') +
                   ' ' + str(b['ticker']).ljust(12, ' ') +
                   ' ' + str(b['figi']).ljust(12, ' ') +
                   ' ' + str(b['lot_qty']-lot_qty+part_qty).ljust(5, ' ') +
                   ' ' + str(b['lot']).ljust(7, ' ') +
                   ' ' + str(b['currency']).ljust(4, ' ') +
                   ' ' + str(b['price']) + '\n')
                    part_qty = lot_qty
            else:
                    f.write(b['time'].strftime('%Y-%m-%d %H:%M:%S') +
                   ' ' + str(b['ticker']).ljust(12, ' ') +
                   ' ' + str(b['figi']).ljust(12, ' ') +
                   ' ' + str(b['lot_qty']).ljust(5, ' ') +
                   ' ' + str(b['lot']).ljust(7, ' ') +
                   ' ' + str(b['currency']).ljust(4, ' ') +
                   ' ' + str(b['price']) + '\n')
    return part_qty

def get_sold():
    b = []
    try:
        with open(g_trial + '/sold.txt', 'r') as f:
            for item in f:
                b.append({'buy_time':datetime(int(item[0:4]), int(item[5:7]), int(item[8:10]), int(item[11:13]), int(item[14:16]), int(item[17:19])),
                          'sell_time':datetime(int(item[21:25]), int(item[26:28]), int(item[29:31]), int(item[32:34]), int(item[35:37]), int(item[38:40])),
                          'ticker':item[41:54].rstrip(),
                          'figi':item[54:67].rstrip(),
                          'lot_qty':int(item[67:73]),
                          'lot':int(item[73:81]),
                          'currency':item[81:84],
                          'buy_price':float(item[86:96]),
                          'sell_price':float(item[97:108]),
                          'profit':float(item[108:].rstrip())
                          })
    except FileNotFoundError:
        return b
    return b

def print_dict(v_dict, prefix = ''):
    res = ''
    for i in sorted(list(v_dict.keys())):
        res = res + prefix + str(i) + ': ' + str(v_dict[i]) + '\n'
    return res

def update_balance(amount, currency):
    b = {}
    try:
        f = open(g_trial+'/balances.txt', 'r')
        for line in f:
            b[line[0:3]] = line[4:].strip()
        f.close()
    except FileNotFoundError:
        b['RUB'] = 0
        b['USD'] = 0
        b['EUR'] = 0
    try:
        b[currency] = round(float(b[currency]) + amount, 2)
    except KeyError:
        b[currency] = amount

    with open(g_trial+'/balances.txt', 'w') as g:
        for curr in b.keys():
            g.write(curr + '=')
            g.write(str(b[curr])+'\n')
    return b[currency]

def get_balance(currency):
    b = {}
    try:
        f = open(g_trial+'/balances.txt', 'r')
        for line in f:
            b[line[0:3]] = line[4:].strip()
        f.close()
    except FileNotFoundError:
        b['RUB'] = 0
        b['USD'] = 0
        b['EUR'] = 0
    return b[currency]

def get_statistic():
    global g_bougth_value
    b = {}
    try:
        f = open(g_trial+'/balances.txt', 'r')
        for line in f:
            b['Balance ' + line[0:3]] = line[4:].strip()
        f.close()
    except FileNotFoundError:
        b['Balance RUB'] = 0
        b['Balance USD'] = 0
        b['Balance EUR'] = 0
    b['Bought RUB'] = 0
    b['Bought USD'] = 0
    b['Bought EUR'] = 0
    b['Bought value RUB'] = 0
    b['Bought value USD'] = 0
    b['Bought value EUR'] = 0
    for i in (get_bought()):
        b['Bought '+i['currency']] = b['Bought '+i['currency']] + i['price'] * i['lot_qty']* i['lot']
        try:
            b['Bought value '+i['currency']] = b['Bought value '+i['currency']] + g_bougth_value[i['ticker']] * i['lot_qty']* i['lot']
        except KeyError:
            None
    b['Balance&Bought RUB'] = float(b['Balance RUB']) + float(b['Bought RUB'])
    b['Balance&Bought USD'] = float(b['Balance USD']) + float(b['Bought USD'])
    b['Balance&Bought EUR'] = float(b['Balance EUR']) + float(b['Bought EUR'])
    b['Profit RUB'] = 0
    b['Profit USD'] = 0
    b['Profit EUR'] = 0
    for i in (get_sold()):
        b['Profit '+i['currency']] = b['Profit '+i['currency']] + i['profit']
    return b

def update_statistic (stat_dict, event, qty=1):
    try:
        stat_dict[event] = stat_dict[event] + qty
    except KeyError:
        stat_dict[event] = qty
    return stat_dict

def find_and_buy():
    result_statistic = {}
    try:
        mkt = client.market.market_stocks_get()
    except Exception as err:
        output('Can''t get stocks list: ' + str(err))
        log('Can''t get stocks list: ' + str(err), 'error_log.txt')
        return result_statistic
    
    bought_list = get_bought()
    sold_list = get_sold()
    result_statistic['Go to checks'] = 0

    try: #MindSpread
        v_max_spread = float(g_trial_params['MAX_SPREAD'])
    except KeyError:
        v_max_spread = 1000000
        
    # Get my portfolio
    try:
        portfolio_response = client.portfolio.portfolio_get()
    except Exception as err:
        output('Can''t get my portfolio: ' + str(err))
        log('Can''t get my portfolio: ' + str(err), 'error_log.txt')
        return result_statistic
    
    # Cycle on stocks
    for i in (getattr(getattr(mkt, 'payload'), 'instruments')):
        should_i_stop()
        update_statistic(result_statistic, 'Total')

        #Skip old Tickers
        if getattr(i, 'ticker')[-3:] == 'old':
            output(getattr(i, 'ticker') + ' old ticker')
            update_statistic(result_statistic, 'Old ticker')
            continue

        #Skip 'min_price_increment': None
        if getattr(i, 'min_price_increment') == None:
            output(getattr(i, 'ticker') + ' min_price_increment: None')
            update_statistic(result_statistic, 'Min_price_increment: None')
            continue
        
        # Check for already requested and bought
        if getattr(i, 'ticker') in [c['ticker'] for c in bought_list]:
            output(getattr(i, 'ticker') + ' already bought')
            update_statistic(result_statistic, 'Already bought')
            continue
        if getattr(i, 'ticker') in [c['ticker'] for c in get_request()]:
            output(getattr(i, 'ticker') + ' already requested')
            update_statistic(result_statistic, 'Already requested')
            continue
        # Check for my portfolio
        if g_trial_params['ENVIRONMENT'] == 'PROD' \
           and getattr(i, 'figi') in [getattr(c, 'figi') for c in getattr(getattr(portfolio_response, 'payload'), 'positions')]:
            output(getattr(i, 'ticker') + ' in my investment portfolio')
            update_statistic(result_statistic, 'In my investment portfolio')
            continue
        
        #Past experienced checks
        if getattr(i, 'ticker') in g_not_available:
            output(getattr(i, 'ticker') + ' NotAvailableForTrading (Past experience)')
            update_statistic(result_statistic, 'NotAvailableForTrading (Past experience)')
            continue

        try:
            if (g_stock_price[getattr(i, 'ticker')] > float(g_trial_params['EXPENSIVE_USD']) and getattr(i, 'currency') in ['USD','EUR']) \
                    or (g_stock_price[getattr(i, 'ticker')] > float(g_trial_params['EXPENSIVE_RUB']) and getattr(i, 'currency') == 'RUB'):
                output(getattr(i, 'ticker') + ' Too expensive ' + getattr(i, 'currency') + ' (Past experience)')
                update_statistic(result_statistic, 'Too expensive ' + getattr(i, 'currency') + ' (Past experience)')
                continue
        except KeyError:
            None
       
        # After all offline checks: one pause every four processed stocks
        if result_statistic['Total'] % int(g_params['SLEEP_PERIOD']) == 0: #TBD Go to checks
            time.sleep(1)

        # Let's pause to sell PROD
        if result_statistic['Total'] % int(g_params['SELL_PROD_PERIOD']) == 0:
            sell_prod()
            if g_trial_params['ENVIRONMENT'] == 'PROD':
                sold_list = get_sold()
                
        try:
            response = client.market.market_orderbook_get(getattr(i, 'figi'), 2)
        except Exception as err:
            output(getattr(i, 'ticker') + ' market_orderbook_get: ' + str(err))
            log(getattr(i, 'ticker') + ' market_orderbook_get: ' + str(err), 'error_log.txt')
            update_statistic(result_statistic, 'Error')
            continue

        if getattr(getattr(response, 'payload'), 'trade_status') != 'NormalTrading':
            output(getattr(i, 'ticker') + ' ' + getattr(getattr(response, 'payload'), 'trade_status'))
            update_statistic(result_statistic, getattr(getattr(response, 'payload'), 'trade_status'))
            if getattr(getattr(response, 'payload'), 'trade_status') == 'NotAvailableForTrading':
                g_not_available.append(getattr(i, 'ticker'))
            continue

        lot_qty = 1
        lot = int(getattr(i, 'lot'))
        # The Cheapest offer in orderbook
        try:
            ask_price = float(getattr(getattr(getattr(response, 'payload'), 'asks')[0], 'price'))
            g_stock_price[getattr(i, 'ticker')] = ask_price*lot
            ask_qty = int(getattr(getattr(getattr(response, 'payload'), 'asks')[0], 'quantity'))
            bid_price = float(getattr(getattr(getattr(response, 'payload'), 'bids')[0], 'price')) #MindSpread
        except IndexError:
            output(getattr(i, 'ticker') + ' IndexError: list index out of range')
            ##print(getattr(i, 'ticker') + ' ' + str(response))
            update_statistic(result_statistic, 'IndexError: list index out of range')
            continue
        
        if not ask_price:
            output('No price')
            print(str(response))
            update_statistic(result_statistic, 'No price')
            continue

        

        if (ask_price * lot > float(g_trial_params['EXPENSIVE_USD']) and getattr(i, 'currency') in ['USD','EUR']) \
                    or (ask_price * lot > float(g_trial_params['EXPENSIVE_RUB']) and getattr(i, 'currency') == 'RUB'):
            output(getattr(i, 'ticker') + ' ' + str(ask_price) + '*' + str(lot) + ' ' + getattr(i, 'currency') + ' Too expensive')
            update_statistic(result_statistic, 'Too expensive ' + getattr(i, 'currency'))
            continue

        if ask_price * lot > float(get_balance(getattr(i, 'currency'))):
            output(getattr(i, 'ticker') + ' ' + str(ask_price) + '*' + str(lot) + ' ' + getattr(i, 'currency') + ' Not enough money')
            update_statistic(result_statistic, 'Not enough money')
            continue

        if (ask_price-bid_price)/ask_price > v_max_spread: #MindSpread
            output(getattr(i, 'ticker') + ': ' + str(ask_price) + '-' + str(bid_price) + ' Spread too wide')
            update_statistic(result_statistic, 'Spread too wide')
            continue

        #Buy_several_stocks
        if ask_price * lot * 2 <= float(get_balance(getattr(i, 'currency'))) \
           and ask_price * lot * 2 <= float(get_balance(getattr(i, 'currency'))) \
           and ask_price * lot * 2 <= float(g_trial_params['EXPENSIVE_USD']) and getattr(i, 'currency') in ['USD','EUR'] \
           and ask_qty >= 2:
            lot_qty = 2

        # Check for already sold
        v_already_sold_str = getattr(i, 'ticker') + ' already sold\n'
        already_sold_flag = 'N'
        for sold in sold_list:
##            if sold['figi'] == getattr(i, 'figi'):
##                v_already_sold_str = v_already_sold_str + '   ' +str(sold['sell_time']) + ' ' + str(ask_price) + ' ' + str(ask_price + 2 * get_comission(ask_price)) + '<>' + str(sold['sell_price']) + '\n'
            if sold['figi'] == getattr(i, 'figi') \
               and (datetime.now() - sold['sell_time']).total_seconds() < float(g_trial_params['SELL_TRACKING_HOURS']) * 60 * 60 \
               and ask_price + 2 * get_comission(ask_price) > sold['sell_price']:
                v_already_sold_str = v_already_sold_str + '   ' +str(sold['sell_time']) + ' ' + str(ask_price) + ' ' + str(ask_price + 2 * get_comission(ask_price)) + '>' + str(sold['sell_price']) + '\n'
                already_sold_flag = 'Y'
        if already_sold_flag == 'Y':
##            v_already_sold_str = v_already_sold_str + '   Already sold\n'
##            if g_trial_params['ENVIRONMENT'] == 'PROD':
##                log(v_already_sold_str, g_trial+'/Already_sold_log.txt')
            log(v_already_sold_str)
            update_statistic(result_statistic, 'Already sold')
            continue

        # Apply checks
        update_statistic(result_statistic, 'Go to checks')
        checks_pass = ''
        try:
            with open(g_trial+'/check_curve_c.txt', 'r') as check_file:
                check_params = {line.split('=')[0] : line.split('=')[1].strip() for line in check_file}
                q = check_find_curve_c(getattr(i, 'figi'),
                                     int(check_params['DAYS']),
                                     check_params['PERIOD'],
                                     ask_price,
                                     int(check_params['DESCENT_PERC']),
                                     int(check_params['ADVANCE_PERC']),
                                     int(check_params['TIMES']))
                if q:
                    checks_pass = checks_pass + 'check_curve_c passed:\n' + print_dict(q, '                   ') + '\n'
                    v_high_level = float(q['1_high_value'])
                    v_low_level = float(q['1 low_value'])
                else:
                    checks_pass = ''
                    continue
        except FileNotFoundError:
            None

        try:
            with open(g_trial+'/check_curve.txt', 'r') as check_file:
                check_params = {line.split('=')[0] : line.split('=')[1].strip() for line in check_file}
                q = check_find_curve(getattr(i, 'figi'),
                                     int(check_params['DAYS']),
                                     check_params['PERIOD'],
                                     ask_price,
                                     int(check_params['DESCENT_PERC']),
                                     int(check_params['ADVANCE_PERC']),
                                     int(check_params['TIMES']))
                if q:
                    checks_pass = checks_pass + 'check_curve passed:\n' + print_dict(q, '                   ') + '\n'
                    v_high_level = float(q['1_high_value'])
                    v_low_level = float(q['1 low_value'])
                else:
                    checks_pass = ''
                    continue
        except FileNotFoundError:
            None

        try:
            with open(g_trial+'/check_level.txt', 'r') as check_file:
                check_params = {line.split('=')[0] : line.split('=')[1].strip() for line in check_file}
                q = check_level(getattr(i, 'figi'),
                                int(check_params['START_PEROD_DAYS']),
                                int(check_params['END_PEROD_DAYS']),
                                check_params['PERIOD'],
                                v_high_level,
                                int(check_params['HIGH_LEVEL_QTY']),
                                v_low_level,
                                int(check_params['LOW_LEVEL_QTY']),)
                if q:
                    checks_pass = checks_pass + 'check_level passed:\n' + print_dict(q, '                   ') + '\n'
                else:
                    checks_pass = ''
                    continue
        except FileNotFoundError:
            None

            
        if checks_pass:
##            log('Go to request to buy: ' + getattr(i, 'ticker') + ', ' + str(ask_qty), g_trial+'/log.txt')
            requested_qty = request(getattr(i, 'ticker'), getattr(i, 'figi'), lot_qty, lot, getattr(i, 'currency'), ask_price, 'Buy')
            if requested_qty > 0:
                log('Request to buy: ' + getattr(i, 'ticker') + '\n' + checks_pass + '\n', g_trial+'/log.txt')
                update_statistic(result_statistic, 'Buy requests events')
                update_statistic(result_statistic, 'Buy requests stocks', requested_qty)
                # Update balance before request execution
                log_str = 'Update balance: ' + str(get_balance(getattr(i, 'currency'))) + ' - ' + str(lot_qty*lot*ask_price + get_comission(lot_qty*lot*ask_price))
                update_balance(-1*(lot_qty*lot*ask_price + get_comission(lot_qty*lot*ask_price)), getattr(i, 'currency')) #Commission_during_buying
                log_str = log_str + ' = ' + str(get_balance(getattr(i, 'currency')))
                log(log_str, g_trial+'/log.txt')
##                if g_trial_params['ENVIRONMENT'] == 'PROD':
##                    log(v_already_sold_str, g_trial+'/Already_sold_log.txt')
    return result_statistic

def check_and_sell(profit):
    global g_bougth_value
    g_bougth_value = {}
    result_statistic = {}
    n = 0

    try: #SellStocksWithLoss
        v_loss_threshold = float(g_trial_params['LOSS'])
    except KeyError:
        v_loss_threshold = 0

    try: #SellStocksWithLoss
        v_max_loss = float(g_trial_params['MAX_LOSS'])
    except KeyError:
        v_max_loss = 0

    try: #MindSpread
        v_max_spread = float(g_trial_params['MAX_SPREAD'])
    except KeyError:
        v_max_spread = 1000000

    for stock in get_bought(): 
        n = n + 1
        try:
            response = client.market.market_orderbook_get(stock['figi'], 2)
        except Exception as err:
            output(stock['ticker'] + ' market_orderbook_get: ' + str(err))
            log(stock['ticker'] + ' market_orderbook_get: ' + str(err), 'error_log.txt')
            continue
        try:
            bid_price = float(getattr(getattr(getattr(response, 'payload'), 'bids')[0], 'price'))
            g_bougth_value[stock['ticker']] = bid_price
            ask_price = float(getattr(getattr(getattr(response, 'payload'), 'asks')[0], 'price')) #MindSpread
        except IndexError:
            output('IndexError: list index out of range')
            print(stock['ticker'] + ' ' + str(response) + '\n')
            g_bougth_value[stock['ticker']] = float(getattr(getattr(response, 'payload'), 'last_price'))
            continue

        if (stock['price'] * stock['lot_qty'] * stock['lot'] + get_comission(stock['price'] * stock['lot_qty'] * stock['lot'])) * (1+float(g_trial_params['PROFIT'])) <= \
           bid_price * stock['lot_qty'] * stock['lot'] - get_comission(bid_price * stock['lot_qty'] * stock['lot']):
            requested_qty = request(stock['ticker'], stock['figi'], stock['lot_qty'], stock['lot'], stock['currency'], stock['price'], 'Sell', bid_price)
            if requested_qty > 0:
                log('Request to sell: ' + stock['ticker'] + ' ' + str(stock['price']) + ' ' + str(bid_price), g_trial+'/log.txt')
                update_statistic(result_statistic, 'Sell requests events')
                update_statistic(result_statistic, 'Sell requests stocks', requested_qty)
        #SellStocksWithLoss
        elif v_loss_threshold > 0 and \
               (stock['price'] * stock['lot_qty'] * stock['lot'] - get_comission(stock['price'] * stock['lot_qty'] * stock['lot'])) > \
               (bid_price * stock['lot_qty'] * stock['lot'] + get_comission(bid_price * stock['lot_qty'] * stock['lot'])) * (1+v_loss_threshold) and \
               (stock['price'] * stock['lot_qty'] * stock['lot'] - get_comission(stock['price'] * stock['lot_qty'] * stock['lot'])) < \
               (bid_price * stock['lot_qty'] * stock['lot'] + get_comission(bid_price * stock['lot_qty'] * stock['lot'])) * (1+v_max_loss) and \
               (ask_price-bid_price)/ask_price <= v_max_spread: 
            #log(stock['ticker'] + ' SellStocksWithLoss: old_price=' + str(stock['price']) + ', new=' + str(bid_price) + ' n%=' + str((bid_price * stock['lot_qty'] * stock['lot'] + get_comission(bid_price * stock['lot_qty'] * stock['lot'])) * (1+v_loss_threshold)), g_trial+'/log.txt')
            requested_qty = request(stock['ticker'], stock['figi'], stock['lot_qty'], stock['lot'], stock['currency'], stock['price'], 'Sell', bid_price)
            if requested_qty > 0:
                log('Request to sell with loss: ' + stock['ticker'] + ' ' + str(stock['price']) + ' ' + str(bid_price), g_trial+'/log.txt')
                update_statistic(result_statistic, 'Sell requests events')
                update_statistic(result_statistic, 'Sell requests stocks', requested_qty)
        if n % int(g_params['SLEEP_PERIOD']) == 0:
            time.sleep(1) 
    return result_statistic

def request(ticker, p_figi, lot_qty, lot, currency, buy_price, req_type, sell_price=''):
    order_id = ''
    order_status = ''
    if g_trial_params['ENVIRONMENT'] == 'PROD':
        v_price = buy_price if req_type == 'Buy' else sell_price
        try:
            order_response = client.orders.orders_limit_order_post(figi=p_figi,
                                                                   limit_order_request={"lots": lot_qty,
                                                                                        "operation": req_type,
                                                                                        "price": v_price})
            order_id = getattr(getattr(order_response, 'payload'), 'order_id')
            order_status = getattr(getattr(order_response, 'payload'), 'status')
            log(order_response, g_trial+'/log.txt')
        except Exception as err: 
            output('Reqest error. ' + ticker + ' ' + req_type + ' ' + str(lot_qty) + ' lots: ' + str(err))
            log('Reqest error. ' + ticker + ' ' + req_type + ' ' +str(lot_qty) + ' lots: ' + str(err), 'error_log.txt')
            return 0
    elif g_trial_params['ENVIRONMENT'] == 'TEST':
        order_status = 'New'
        
    if order_status == 'New':
        with open(g_trial + '/request.txt', 'a') as g:
                g.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                       ' ' + str(ticker).ljust(12, ' ') +
                       ' ' + str(p_figi).ljust(12, ' ') +
                       ' ' + str(lot_qty).ljust(5, ' ') +
                       ' ' + str(lot).ljust(7, ' ') +
                       ' ' + str(currency).ljust(4, ' ') +
                       ' ' + str(buy_price).ljust(10, ' ') +
                       ' ' + str(req_type).ljust(4, ' ')  +
                       ' ' + str(sell_price).ljust(10, ' ')  +  '\n')
        return lot_qty
    else:
        log(ticker + ' ' + req_type + ' request status: ' + order_status, g_trial+'/log.txt')
        return 0

def get_request():
    b = []
    try:
        with open(g_trial + '/request.txt', 'r') as f:
            for item in f:
                r = {'time':datetime(int(item[0:4]), int(item[5:7]), int(item[8:10]), int(item[11:13]), int(item[14:16]), int(item[17:19])),
                          'ticker':item[20:33].rstrip(),
                          'figi':item[33:46].rstrip(),
                          'lot_qty':int(float(item[46:52])),
                          'lot':int(item[52:60]),
                          'currency':item[60:63],
                          'buy_price':float(item[65:76].rstrip()),
                          'type':item[76:81].rstrip()
                          }
                if item[81:].rstrip():
                    r['sell_price'] = float(item[81:].rstrip())
                b.append(r)
    except FileNotFoundError:
        return b
    return b


def check_requests():
    #log('In check_requests', 'debug.txt') # TBD
    res = {}
    rr = get_request()
    bought = {} # Already bought
    for  i in get_bought():
        try:
            bought[i['figi']] = bought[i['figi']] + i['lot_qty']
        except KeyError:
            bought[i['figi']] = i['lot_qty']
    if g_trial_params['ENVIRONMENT'] == 'PROD':
        try:
            response = client.portfolio.portfolio_get()
            my_portfolio = {getattr(c, 'figi'):int(getattr(c, 'balance')) for c in getattr(getattr(response, 'payload'), 'positions')}
        except Exception as err:
            output('Can''t get portfolio: ' + str(err))
            log('Can''t get portfolio: ' + str(err), 'error_log.txt')
            return res
        
    with open(g_trial + '/request.txt', 'w') as f:
        for r in rr:
              if (datetime.now()-r['time']).total_seconds() > 60*60*24: # Expires after 24 hours
                  with open(g_trial + '/rejected_requests.txt', 'a') as rf:
                      try:
                          sell_price_str = ' ' + str(r['sell_price']).ljust(10, ' ')
                      except KeyError:
                          sell_price_str = ''
                      rf.write(r['time'].strftime('%Y-%m-%d %H:%M:%S') +
                         ' ' + str(r['ticker']).ljust(12, ' ') +
                         ' ' + str(r['figi']).ljust(12, ' ') +
                         ' ' + str(r['lot_qty']).ljust(5, ' ') +
                         ' ' + str(r['lot']).ljust(7, ' ') +
                         ' ' + str(r['currency']).ljust(4, ' ') +
                         ' ' + str(r['buy_price']).ljust(10, ' ') +
                         ' ' + str(r['type'].ljust(4, ' ')) + sell_price_str + '\n')
                      update_statistic(res, 'Rejected requests')
                      # Money returning
                      if r['type'] == 'Buy':
                          update_balance(r['lot_qty'] * r['lot'] * r['buy_price'] + get_comission(r['lot_qty'] * r['lot'] * r['buy_price']), r['currency']) #Commission_during_buying
              elif r['type'] == 'Buy':
                  if g_trial_params['ENVIRONMENT'] == 'PROD':
                      try:
                         already_bougth = bought[r['figi']]
                      except KeyError:
                         already_bougth = 0
                      try:
                         buy_qty = int(my_portfolio[r['figi']] / r['lot'] - already_bougth)
                      except KeyError:
                         buy_qty = 0

                      if buy_qty > r['lot_qty']:
                          update_statistic(res, 'Requests with error')
                          log(r['ticker'] + ' bougth more than requested: ' + str(buy_qty) + ' > ' + str(r['lot_qty']))
                  elif g_trial_params['ENVIRONMENT'] == 'TEST':
                      buy_qty = r['lot_qty']
                     
                  if buy_qty > 0:
                      with open(g_trial + '/bought.txt', 'a') as sf:
                          sf.write(r['time'].strftime('%Y-%m-%d %H:%M:%S') +
                                  ' ' + str(r['ticker']).ljust(12, ' ') +
                                  ' ' + str(r['figi']).ljust(12, ' ') +
                                  ' ' + str(buy_qty).ljust(5, ' ') +
                                  ' ' + str(r['lot']).ljust(7, ' ') +
                                  ' ' + str(r['currency']).ljust(4, ' ') +
                                  ' ' + str(r['buy_price']).ljust(10, ' ') + '\n')
                      update_statistic(res, 'Buy requests completed')
                      update_statistic(res, 'Stocks bought', buy_qty)
                      log(r['ticker'] + ' bougth: ' + str(buy_qty), g_trial+'/log.txt')
                  if r['lot_qty'] > buy_qty:
                          f.write(r['time'].strftime('%Y-%m-%d %H:%M:%S') +
                         ' ' + str(r['ticker']).ljust(12, ' ') +
                         ' ' + str(r['figi']).ljust(12, ' ') +
                         ' ' + str(r['lot_qty']-buy_qty).ljust(5, ' ') +
                         ' ' + str(r['lot']).ljust(7, ' ') +
                         ' ' + str(r['currency']).ljust(4, ' ') +
                         ' ' + str(r['buy_price']).ljust(10, ' ') +
                         ' ' + str(r['type']) + '\n')
              elif r['type'] == 'Sell':
                  if g_trial_params['ENVIRONMENT'] == 'PROD':
                      try:
                         sell_qty = r['lot_qty'] - int(my_portfolio[r['figi']] / r['lot'])
                      except KeyError:
                         sell_qty = r['lot_qty']
                  elif g_trial_params['ENVIRONMENT'] == 'TEST':
                      sell_qty = r['lot_qty']
                  
                  
                  if sell_qty > 0:
                      sold_qty = sell(r['ticker'], sell_qty, r['sell_price'])
                      if sold_qty != sell_qty:
                          log('Error! Faild to sell necessary amount. ' + r['ticker'] + ', sold=' + str(sold_qty) + ', necessary=' + str(sell_qty))
                      update_statistic(res, 'Sell requests completed')
                      update_statistic(res, 'Stocks sold', sold_qty)
                      log_str = 'Update balance: ' + str(get_balance(r['currency'])) + ' + ' + str(sold_qty * r['lot'] * r['sell_price'] - get_comission(sold_qty * r['lot'] * r['sell_price']))
                      update_balance(sold_qty * r['lot'] * r['sell_price'] -
##                                     get_comission(sold_qty * r['lot'] * r['buy_price']) - #Commission_during_buying
                                     get_comission(sold_qty * r['lot'] * r['sell_price'])
                                     , r['currency'])
                      log(r['ticker'] + ' sold: ' + str(sold_qty), g_trial+'/log.txt')
                      log_str = log_str + ' = ' + str(get_balance(r['currency']))
                      log(log_str, g_trial+'/log.txt')
                  if r['lot_qty'] > sell_qty:
                          f.write(r['time'].strftime('%Y-%m-%d %H:%M:%S') +
                         ' ' + str(r['ticker']).ljust(12, ' ') +
                         ' ' + str(r['figi']).ljust(12, ' ') +
                         ' ' + str(r['lot_qty']-sell_qty).ljust(5, ' ') +
                         ' ' + str(r['lot']).ljust(7, ' ') +
                         ' ' + str(r['currency']).ljust(4, ' ') +
                         ' ' + str(r['buy_price']).ljust(10, ' ') +
                         ' ' + str(r['type']).ljust(4, ' ') +
                         ' ' + str(r['sell_price']) + '\n')
    return res

def show_all_stat():
    global g_trial
    with open('trials.txt', 'r') as trials_file:
        trials = [line.strip() for line in trials_file]
    for trial in trials:
        if not trial.rstrip(): #Skip empty rows
            continue
        g_trial = trial
        output('\n' + 'Statistic:\n' + print_dict(get_statistic(), '          '))

def sell_prod():
    global g_trial, g_trial_params, client
    tmp_trial = g_trial
    tmp_trial_params = g_trial_params

    for trial in set(trials):
        if not trial.rstrip(): #Skip empty rows
            continue
        with open(trial+'/trial_params.txt', 'r') as trial_params_file:
            g_trial_params = {line.split('=')[0] : line.split('=')[1].strip() for line in trial_params_file}
            g_trial = trial
        if g_trial_params['ENVIRONMENT'] != 'PROD':
            continue
        # Sell
        v_dict = {}
        v_dict = check_and_sell(g_trial_params['PROFIT'])
        if v_dict:
            log('\n' + 'check_and_sell=\n' + print_dict(v_dict, '               '))
        # Requests process
        v_dict = {}
        v_dict = check_requests()
        if v_dict:
            log('\n' + 'check_requests=\n' + print_dict(v_dict, '               '))
        
    # Return original environment
    g_trial = tmp_trial
    g_trial_params = tmp_trial_params  

def trade():
    global g_trial, g_params, g_trial_params, client, g_fmt, g_not_available, g_stock_price, trials
    
    with open('delete_to_stop.txt', 'w') as stp_file:
        stp_file.write(str(datetime.now())+'\n')
    with open('trials.txt', 'r') as trials_file:
        trials = [line.strip() for line in trials_file]
    # Reading common parameters
    try:
        with open('params.txt', 'r') as params_file:
            g_params = {line.split('=')[0] : line.split('=')[1].strip() for line in params_file}
    except FileNotFoundError:
        with open('params.txt', 'w') as params_file:
            params_file.write('PARAM=VALUE')
        print('params.txt created')
        exit(0)
    last_iteration_start_time = datetime(2019, 12, 21, 15, 33, 0)
    log('Starting')
    f = open('token.txt', 'r')
    token = f.read()
    f.close()
    g_fmt = '%Y-%m-%dT%H:%M:%S.%f+03:00'
    g_not_available = []
    g_stock_price = {}
    while 2 > 1:
        # No work at night
        if datetime.now().hour < int(g_params['START_TIME']) and datetime.now().hour > int(g_params['END_TIME']):
            print('No work at night')
            time.sleep(60)
            should_i_stop()
            continue

        # Wait for time gap
        sec_between = (datetime.now() - last_iteration_start_time).total_seconds()
        if sec_between < int(g_params['TIME_GAP'])*60:
            should_i_stop()
            print('Pause for ' + str(int(g_params['TIME_GAP'])*60 - sec_between) + ' sec.')
            time.sleep(60)
            continue
        last_iteration_start_time = datetime.now()

        #Sandbox or PROD
        client = openapi.api_client(token)
        # Process trials
        for trial in trials:
            if not trial.rstrip(): #Skip empty rows
                continue
            g_trial = trial
            should_i_stop()
            # Reading common parameters
            with open('params.txt', 'r') as params_file:
                g_params = {line.split('=')[0] : line.split('=')[1].strip() for line in params_file}
            # Reading trial parameters
            if not os.path.exists(trial): os.makedirs(trial)
            try:
                with open(trial+'/trial_params.txt', 'r') as trial_params_file:
                    g_trial_params = {line.split('=')[0] : line.split('=')[1].strip() for line in trial_params_file}
            except FileNotFoundError:
                with open(trial+'/trial_params.txt', 'w') as trial_params_file:
                    trial_params_file.write('PARAM=VALUE')
                output('trial_params.txt created')
                continue
            # Sell
            v_dict = {}
            v_dict = check_and_sell(g_trial_params['PROFIT'])
            if v_dict:
                log('\n' + 'check_and_sell=\n' + print_dict(v_dict, '               '))
            # Requests process
            v_dict = {}
            v_dict = check_requests()
            if v_dict:
                log('\n' + 'check_requests=\n' + print_dict(v_dict, '               '))
            
            if float(get_balance('USD'))<1 and float(get_balance('EUR'))<1 and float(get_balance('RUB'))<50:
                output('No money left')
            elif datetime.now().hour < int(g_params['START_BUY_TIME']) and datetime.now().hour > int(g_params['END_TIME']):
                output('We are not buying in the morning')
                g_not_available = []
                g_stock_price = {}
            elif g_trial_params['STOP_BUYING'] == 'Y':
                output('Buying is stopped')
            else:
                log('\n' + 'find_and_buy=\n' + print_dict(find_and_buy(), '             '))
            # Requests process
            v_dict = {}
            v_dict = check_requests()
            if v_dict:
                log('\n' + 'check_requests=\n' + print_dict(v_dict, '               '))
            log('\n' + 'Statistic:\n' + print_dict(get_statistic(), '          '))

if __name__ == "__main__":
    trade()
