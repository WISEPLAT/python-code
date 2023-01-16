import trader

global g_trial

with open('trials.txt', 'r') as trials_file:
    trials = [line.strip() for line in trials_file]

for trial in set(trials):
    if not trial.rstrip(): #Skip empty rows
        continue
    trader.g_trial = trial
    trader.g_bougth_value = {}
    print(trial + '\n' + trader.print_dict(trader.get_statistic(), '          ') + '\n')
