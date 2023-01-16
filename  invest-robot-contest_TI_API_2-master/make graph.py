import tinkoff.invest
import intro.basek
import intro.accid
from intro.quotation_dt import quotation_count
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import datetime
import time
from pathlib import Path

hist_candles_brent = pd.read_csv('csv_files/brent062022_report.csv')

with plt.style.context('Solarize_Light2'):
    a = historical_candles_df['time']
    b = historical_candles_df['close']
    c = historical_candles_df['ma']
    d = historical_candles_df['ema']
    plt.plot(a, b, a, c, a, d)
    plt.show()