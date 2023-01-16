from config.personal_data import get_account, get_account_type
from tinkoff.invest import Client
from config.personal_data import get_token
from datetime import datetime, timedelta
import pytz


def check_money(user_id, price, quantity, currency, account_id="", account_type=""):
    if account_id == "":
        account_id = get_account(user_id=user_id)

    if account_type == "":
        account_type = get_account_type(user_id=user_id)

    with Client(get_token(user_id)) as client:
        if account_type == "sandbox":
            positions = client.sandbox.get_sandbox_positions(account_id=account_id)
        else:
            positions = client.operations.get_positions(account_id=account_id)

        for i in positions.money:
            if (i.currency == currency) and ((i.units + (i.nano * 1e-9)) > price * quantity * 1.03):
                return True

    return False


def check_time(user_id, figi):
    # Получаем расписание всех площадок за неделю
    with Client(get_token(user_id)) as client:
        schedules = client.instruments.trading_schedules(
            from_=datetime.utcnow(),
            to=datetime.utcnow() + timedelta(days=6),
        ).exchanges

        # Получаем инструмент
        try:
            security = client.instruments.get_instrument_by(id_type=1, id=figi).instrument
        except Exception as ex:
            print(ex)
            error = "Такой бумаги не существует!"
            return False, error

        # Получаем время сейчас в часовом поясе UTC
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)

        for i in schedules:
            if i.exchange == security.exchange:  # Если совпадают торговые площадки
                for j in i.days:
                    if j.is_trading_day and j.start_time < now < j.end_time:
                        return True, ""
                    elif j.is_trading_day:
                        start_time = j.start_time - now
                        error = (
                            f"Бумаги <b>{security.name}</b>\n"
                            f"FIGI: {security.figi}\n"
                            f"Площадка: {security.exchange}\n"
                            f"До торгов осталось: <b>{start_time}</b>"
                        )
                        return False, error

    return False, "else"
