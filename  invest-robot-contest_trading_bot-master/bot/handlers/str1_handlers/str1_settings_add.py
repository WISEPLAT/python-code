from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config.personal_data import get_account, get_account_type, get_account_access
import sqlite3 as sl
from trading.get_securities import security_by_figi
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.get_securities import security_name_by_figi, get_security_list
from trading.get_account_info import get_currency_sing
from trading.trade_help import get_price_figi

"""

    Тут представлены все хэндлеры, которые отвечают за добавление бумаги в торговую стратегию

"""


"""
    Создаём состояние ожидания
"""


class AddToStr1(StatesGroup):
    wait_sfb = State()


"""
    Запускаем состояние ожидания названия
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:settings:add:start"))
async def str1_add_search(callback_query):

    await bot.send_message(chat_id=callback_query.from_user.id, text="Введите название бумаги или FIGI:")
    await AddToStr1.wait_sfb.set()



@dp.message_handler(state=AddToStr1.wait_sfb)
async def str1_add_choose(message: Message, state: FSMContext):

    security_list = get_security_list(user_id=message.from_user.id, name=message.text)
    if len(security_list) != 0:
        for security in security_list:

            choose_share_keyboard = InlineKeyboardMarkup()
            choose_share_keyboard.add(InlineKeyboardButton(text=f"Добавить", callback_data=f"str1:settings:add:figi:{security.figi}"))

            try:
                inst_type = security.instrument_type

                if inst_type == "share":
                    inst = "Акции"
                elif inst_type == "future":
                    inst = "Фьючерсы"
                elif inst_type == "bond":
                    inst = "Бонды"
                elif inst_type == "etf":
                    inst = "ETF"
                elif inst_type == "currency":
                    inst = "Валюта"
                else:
                    inst = inst_type

            except:
                inst = "Акции"

            await message.answer(
                text=
                f"🧾<b>{inst} {security.name}</b>\n"
                f"FIGI: {security.figi}\n\n"
                f"Бумаг в лоте: {security.lot}\n"
                f"Средняя цена бумаги: {round(get_price_figi(user_id=message.from_user.id, figi=security.figi), 4)}{get_currency_sing(security.currency)}\n"
                f"Итого стоимость: {round(security.lot * get_price_figi(user_id=message.from_user.id, figi=security.figi), 4)}{get_currency_sing(security.currency)}\n"
                , reply_markup=choose_share_keyboard)

            await state.finish()
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"Такой бумаги нет!")
        await bot.send_message(chat_id=message.from_user.id, text=f"Повторите ввод или напишите 'Отмена':")
        return 0


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:settings:add:figi:"))
async def str1_add_finish(callback_query):

    data = callback_query.data.split(":")
    figi = data[4]
    user_id = callback_query.from_user.id
    name = security_name_by_figi(figi, user_id=user_id)
    account_id = get_account(user_id=user_id)
    account_type = get_account_type(user_id=user_id)
    account_access = get_account_access(user_id=user_id)
    currency = security_by_figi(figi=figi, user_id=user_id).currency

    new_str1_sfb = (user_id, account_id, account_type, account_access, figi, name, "False", "False", 0.0, currency, 1, 4, 0.0, 20.0, 0.02, 0.03)

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    info = cursor.execute('SELECT * FROM str1_config WHERE user_id=? AND account_id = ? AND figi = ?', (user_id, account_id, figi))
    if info.fetchone() is None:
        cursor.execute("INSERT INTO str1_config (user_id, account_id, account_type, account_access, figi, name, trade_status, notif_status, buy_price,"
                    "currency, quantity_lots, period, macd_border, adx_border, take_profit, stop_loss) VALUES (?,?,?,"
                       "?,?,?,?,?,?,?,?,?,?,?,?,?)", (new_str1_sfb))
        connection.commit()
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.from_user.id, text="Бумага успешно добавлена!")
    else:
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.from_user.id, text="Бумага уже была добавлена!")