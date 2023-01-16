# Получение списка доступных фьючерсов и их запись в файл
import tinkoff.invest
import intro.basek
import intro.accid
from intro.quotation_dt import quotation_count
# from intro.quotation_dt import moneyvalue_count
from pathlib import Path
import pandas as pd

TOKEN = intro.basek.TINKOFF_INVEST_DOG_NEW
SDK_client = tinkoff.invest.Client(TOKEN)
User_acc_ID = intro.accid.ACC_ID


def futures_list():
    with SDK_client as client:
        fc = client.instruments.futures(instrument_status=2)
        futur_list = futures_list_structure(fc.instruments)
        return futur_list


def futures_list_structure(instruments: [tinkoff.invest.Future]):
    futures_structure = pd.DataFrame([{
        'name': f.name,
        'figi': f.figi,
        'uid': f.uid,
        'ticker': f.ticker,
        'expiration_date': f.expiration_date,
        'status': f.trading_status,
        'basic_asset_size': quotation_count(f.basic_asset_size),
        'api_trade_available_flag': f.api_trade_available_flag,
        'lot': f.lot,
        'class_code': f.class_code,
        'min_price_increment': quotation_count(f.min_price_increment)
    } for f in instruments])

    return futures_structure


def record_to_csv():
    filepath = Path('csv_files/futures_list.csv')
    df = pd.DataFrame(futures_list())
    df.to_csv(filepath)
    return print('Record complete')


def shares_list():
    with SDK_client as client:
        sc = client.instruments.futures(instrument_status=2)
        shrs_list = shares_list_structure(sc.instruments)
        return shrs_list


def shares_list_structure(instruments: [tinkoff.invest.Share]):
    shares_structure = pd.DataFrame([{
        'name': s.name,
        'figi': s.figi,
        'uid': s.uid,
        'ticker': s.ticker,
        'klong': s.klong,
        'kshort': s.kshort,
        # 'nominal': moneyvalue_count(s.basic_asset_size),
        'api_trade_available_flag': s.api_trade_available_flag,
        'lot': s.lot,
        'class_code': s.class_code,
        'min_price_increment': quotation_count(s.min_price_increment)
    } for s in instruments])

    return shares_structure


def record_shares_to_csv():
    filepath = Path('csv_files/shares_list.csv')
    df = pd.DataFrame(shares_list())
    df.to_csv(filepath)
    return print('Record complete')

print(shares_list())

print(futures_list())

