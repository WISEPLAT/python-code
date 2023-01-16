from main import dp, bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.strategy.str1 import statistic_str1
from config.personal_data import get_account, get_account_access
import sqlite3 as sl
from trading.get_securities import security_name_by_figi

days = 2
week = 4

'''
    Информация по Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:stat"))
async def str1_stat(callback_query):
    data = callback_query.data.split(":")

    user_id = data[3]
    figi = data[4]
    name = security_name_by_figi(figi=figi, user_id=user_id)

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"<b>{name}</b>\n15-минутный график:")

    stat_15 = statistic_str1(figi=figi, period=days, hour_graph=False, user_id=user_id)

    with open(f"img/str1/graph/15_min_{figi}.png", "rb") as graph_15:
        await bot.send_photo(chat_id=callback_query.from_user.id, photo=graph_15)

    with open(f"img/str1/ind/15_min_{figi}.png", "rb") as ind_15:
        await bot.send_photo(chat_id=callback_query.from_user.id, photo=ind_15)

    if stat_15[0]:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📈Цена растёт📈\n{stat_15[1]}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📉Цена падает📉\n{stat_15[1]}")

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"<b>{name}</b>\nЧасовой график:")

    stat_hour = statistic_str1(figi=figi, period=week, hour_graph=True, user_id=user_id)

    with open(f"img/str1/graph/hour_{figi}.png", "rb") as graph_hour:
        await bot.send_photo(chat_id=callback_query.from_user.id, photo=graph_hour)

    with open(f"img/str1/ind/hour_{figi}.png", "rb") as ind_hour:
        await bot.send_photo(chat_id=callback_query.from_user.id, photo=ind_hour)

    if stat_hour[0]:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📈Цена растёт📈\n{stat_hour[1]}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📉Цена падает📉\n{stat_hour[1]}")


'''
    Старт/Стоп Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:trade"))
async def str1_trade_status(callback_query):
    data = callback_query.data.split(":")

    status = data[2]
    user_id = data[3]
    figi = data[4]
    account_id = get_account(user_id=user_id)

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE str1_config SET trade_status=? WHERE user_id = ? AND figi = ? AND account_id = ?",
                   (status, user_id, figi, account_id))
    connection.commit()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=callback_query.message.text, reply_markup=edit_str1_keyboard(user_id, figi))


'''
    Старт/Стоп Стратегии 1 уведомления
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:notif"))
async def str1_notif_status(callback_query):
    data = callback_query.data.split(":")

    status = data[2]
    user_id = data[3]
    figi = data[4]
    account_id = get_account(user_id=user_id)

    conn = sl.connect("db/BotDB.db")
    cur = conn.cursor()
    cur.execute("UPDATE str1_config SET notif_status=? WHERE user_id = ? AND figi = ? AND account_id = ?",
                (status, user_id, figi, account_id))
    conn.commit()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=callback_query.message.text, reply_markup=edit_str1_keyboard(user_id, figi))


"""
    Начало удаления стратегии
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:settings:delete:start"))
async def ema_adx_macd_str1_delete(callback_query):
    user_id = callback_query.from_user.id
    account_id = get_account(user_id)
    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    securities = cursor.execute('SELECT figi, name FROM str1_config WHERE user_id = ? AND account_id = ? ',
                                (user_id, account_id)).fetchall()

    delete_keyboard = InlineKeyboardMarkup()
    if not securities:
        await bot.send_message(chat_id=user_id, text=f"<b>У Вас нет бумаг!</b>")
    else:
        for line in securities:
            delete_keyboard.add(
                InlineKeyboardButton(text=f"Удалить {line[1]}", callback_data=f"str1:settings:delete:choose:{line[0]}"))
        await bot.send_message(chat_id=user_id, text=f"<b>Выберите акции для удаления:</b>",
                               reply_markup=delete_keyboard)


"""
    Конец удаления бумаги из стратегии
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:settings:delete:choose"))
async def ema_adx_macd_str1_delete_finish(callback_query):
    data = callback_query.data.split(":")

    figi = data[4]
    user_id = callback_query.from_user.id
    account_id = get_account(user_id=user_id)

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    cursor.execute('DELETE FROM str1_config WHERE user_id = ? AND account_id = ? AND figi = ? ',
                   (user_id, account_id, figi))
    connection.commit()

    securities = cursor.execute(
        'SELECT figi,name FROM CONFIG WHERE user_id = ? AND account_id = ? ',
        (user_id, account_id)).fetchall()

    delete_keyboard = InlineKeyboardMarkup()
    if not securities:
        await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                    text=f"<b>У Вас нет бумаг!</b>")
    else:
        for line in securities:
            delete_keyboard.add(
                InlineKeyboardButton(text=f"Удалить {line[1]}", callback_data=f"str1:settings:delete:choose:{line[0]}"))
        await bot.edit_message_text(chat_id=user_id, message_id=callback_query.message.message_id,
                                    text=f"<b>Выберите акции для удаления:</b>", reply_markup=delete_keyboard)


"""
    Список всех бумаг, участвующих в торговле
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:list"))
async def str1_list(callback_query):
    user_id = callback_query.from_user.id
    account_id = get_account(user_id)

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    securities = cursor.execute('SELECT figi,name,trade_status,notif_status FROM str1_config WHERE user_id = ? AND '
                                'account_id = ? ',
                                (user_id, account_id)).fetchall()

    for line in securities:

        str1_menu = []

        stat_str1_button = InlineKeyboardButton(text=f"📈",
                                                callback_data=f"str1:stat:show:{user_id}:{line[0]}")

        if line[3] == "True":
            status_notif_button = InlineKeyboardButton(text=f"🔔",
                                                       callback_data=f"str1:notif:False:{user_id}:{line[0]}")
        else:
            status_notif_button = InlineKeyboardButton(text=f"🔕", callback_data=f"str1:notif:True:{user_id}:{line[0]}")

        if get_account_access(user_id=user_id) == 1:
            if line[2] == "True":
                status_str1_button = InlineKeyboardButton(text=f"⏹",
                                                          callback_data=f"str1:trade:False:{user_id}:{line[0]}")
            else:
                status_str1_button = InlineKeyboardButton(text=f"▶️",
                                                          callback_data=f"str1:trade:True:{user_id}:{line[0]}")

            settings_str1_button = InlineKeyboardButton(text=f"⚙", callback_data=f"str1:config:start:{user_id}:{line[0]}")

            str1_menu.append([stat_str1_button, status_str1_button, status_notif_button, settings_str1_button])

        else:
            str1_menu.append([stat_str1_button, status_notif_button])

        ema_adx_macd_keyboard = InlineKeyboardMarkup(
            inline_keyboard=
            str1_menu,
        )

        await bot.send_message(chat_id=user_id, text=f"<b>{line[1]}</b>", reply_markup=ema_adx_macd_keyboard)


def edit_str1_keyboard(user_id, figi):

    account_id = get_account(user_id)
    conn = sl.connect("db/BotDB.db")
    cur = conn.cursor()

    share = cur.execute(
        'SELECT name,trade_status,notif_status FROM str1_config WHERE user_id = ? AND account_id = ? AND figi = ? ',
        (user_id, account_id, figi)).fetchone()

    str1_menu = []

    stat_str1_button = InlineKeyboardButton(text=f"📈",
                                            callback_data=f"str1:stat:show:{user_id}:{figi}")

    if share[2] == "True":
        status_notif_button = InlineKeyboardButton(text=f"🔔",
                                                   callback_data=f"str1:notif:False:{user_id}:{figi}")
    else:
        status_notif_button = InlineKeyboardButton(text=f"🔕", callback_data=f"str1:notif:True:{user_id}:{figi}")

    if get_account_access(user_id=user_id) == 1:
        if share[1] == "True":
            status_str1_button = InlineKeyboardButton(text=f"⏹",
                                                      callback_data=f"str1:trade:False:{user_id}:{figi}")
        else:
            status_str1_button = InlineKeyboardButton(text=f"▶️",
                                                      callback_data=f"str1:trade:True:{user_id}:{figi}")

        settings_str1_button = InlineKeyboardButton(text=f"⚙", callback_data=f"str1:config:start:{user_id}:{figi}")

        str1_menu.append([stat_str1_button, status_str1_button, status_notif_button, settings_str1_button])

    else:
        str1_menu.append([stat_str1_button, status_notif_button])

    ema_adx_macd_keyboard = InlineKeyboardMarkup(
        inline_keyboard=
        str1_menu,
    )

    return ema_adx_macd_keyboard
