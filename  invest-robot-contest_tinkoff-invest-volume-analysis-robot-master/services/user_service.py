import logging

from tinkoff.invest import Client
from tinkoff.invest.utils import now

from settings import TOKEN, IS_SANDBOX, INSTRUMENTS

logger = logging.getLogger(__name__)


def get_instrument_by_asset(asset, instruments):
    futures = list(
        filter(lambda item: item.basic_asset == asset and now() < item.last_trade_date, instruments))
    futures.sort(key=lambda item: item.last_trade_date)
    return futures


class UserService:
    def show_settings(self):
        if not TOKEN:
            print("Не задан токен профиля для Тинькофф Инвестиций. Проверьте общие настройки приложения")
            exit()

        try:
            with Client(TOKEN) as client:
                if IS_SANDBOX:
                    print("Установлен режим работы с песочницей.\n")
                    response = client.sandbox.get_sandbox_accounts()
                else:
                    print("Установлен режим работы с реальным счетом.\n")
                    response = client.users.get_accounts()

                print("Список счетов:")
                for account in response.accounts:
                    print(
                        f"name=[{account.name}], opened=[{account.opened_date}], status=[{account.status}], id=[{account.id}]"
                    )
                print()

                print("Актуальный список фьючерсов по выбранным активам:")
                response = client.instruments.futures()
                for instrument in INSTRUMENTS:
                    asset = instrument["alias"] if "alias" in instrument else instrument["name"]
                    futures = get_instrument_by_asset(asset, response.instruments)
                    print(f"{instrument['name']}:")
                    for future in futures:
                        print(f"name=[{future.name}], ticker=[{future.ticker}], figi=[{future.figi}]")
                    print()

                input("Сверьте настройки приложения и нажмите Enter...")
        except Exception as ex:
            logger.error(ex)
