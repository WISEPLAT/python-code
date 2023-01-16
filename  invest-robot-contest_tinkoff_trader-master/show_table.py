import trader
import os

global g_trial

def get_table():
    with open('trials.txt', 'r') as trials_file:
        trials = [line.strip() for line in trials_file]
    sold_pile = {}
    days = []
    res_table = {}
    currencies = ['USD', 'RUB', 'EUR']
    for trial in set(trials):
        if not trial.rstrip(): #Skip empty rows
            continue
        trader.g_trial = trial
        sold = trader.get_sold()
        sold_pile[trial] = sold
        for s in sold:
            days.append(s['sell_time'].replace(hour=0, minute=0, second=0, microsecond=0))
    days = set(days)

    # Init empty table
    for d in days:
        empty_record = {}
        for trial in sold_pile.keys():
            trial_empty_record = {}
            for c in currencies:
                trial_empty_record[c] = 0
            empty_record[trial] = trial_empty_record
        res_table[d] = empty_record

    # Fill table
    for trial in sold_pile.keys():
        for sell in sold_pile[trial]:
            res_table[sell['sell_time'].replace(hour=0, minute=0, second=0, microsecond=0)][trial][sell['currency']] = res_table[sell['sell_time'].replace(hour=0, minute=0, second=0, microsecond=0)][trial][sell['currency']] + sell['profit']
    return res_table

def out_put(p_str, p_target):
    print(p_str)
    if p_target != '':
        with open(p_target, 'a') as f:
            f.write(p_str)
    
    
def show_table(p_currency, p_target):
    column_width = 15

    if p_target:
        try:
            os.remove(p_target)
        except FileNotFoundError:
            None

    t = get_table()
    total = {}
    for d in sorted(t.keys()):
        trials = sorted(t[d].keys())
        break
    header = ''
    for trial in trials: 
      header = header + trial.rjust(column_width, ' ') + ' '
      total[trial] = 0
    out_put('           '+header+'\n', p_target)
    
    for d in sorted(t.keys()):
        v_str = ''
        for trial in trials:
            v_str =  v_str + str(round(t[d][trial][p_currency], 2)).rjust(column_width, ' ') + ' '
            total[trial] = total[trial] + t[d][trial][p_currency]
        out_put(d.strftime('%d.%m.%Y')+' '+v_str+'\n', p_target)

    footer = ''
    for trial in trials: 
      footer = footer + str(round(total[trial], 2)).rjust(column_width, ' ') + ' '
    out_put('Total:     '+footer+'\n', p_target)


show_table('USD', 'table_usd.txt')
show_table('RUB', 'table_rub.txt')

