from main import dp, bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.personal_data import get_account
import sqlite3 as sl
from trading.get_securities import security_name_by_figi

'''
    Информация по Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:config:start:"))
async def str1_config_start(callback_query):
    data = callback_query.data.split(":")

    user_id = data[3]
    figi = data[4]
    account_id = get_account(user_id)
    name = security_name_by_figi(figi=figi, user_id=user_id)

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Редактирование стратегии для <b>{name}</b>")

    str1_conf = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text=f"-1", callback_data=f"str1:config:edit:-1:{figi}"),
                InlineKeyboardButton(text=f"+1", callback_data=f"str1:config:edit:+1:{figi}"),
                InlineKeyboardButton(text=f"✔", callback_data=f"str1:config:set:{figi}"),
            ]
        ],
    )

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()
    data = cursor.execute(
        "SELECT quantity_lots, take_profit, stop_loss FROM str1_config WHERE user_id = ? AND figi = ? AND account_id = ?",
        (user_id, figi, account_id)).fetchone()

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Количество лотов: {data[0]}",
                           reply_markup=str1_conf)
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Тейк-профит(%): {int(data[1] * 100)}",
                           reply_markup=str1_conf)
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Стоп-лосс(%): {int(data[2] * 100)}",
                           reply_markup=str1_conf)


'''
    Старт/Стоп Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:config:edit:"))
async def str1_config_edit(callback_query):
    data = callback_query.data.split(":")

    status = callback_query.message.text.split(":")

    edit = data[3]
    figi = data[4]

    new_data = float(status[1]) + float(edit)

    str1_conf = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text=f"-1", callback_data=f"str1:config:edit:-1:{figi}"),
                InlineKeyboardButton(text=f"+1", callback_data=f"str1:config:edit:+1:{figi}"),
                InlineKeyboardButton(text=f"✔", callback_data=f"str1:config:set:{figi}"),
            ]
        ],
    )

    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"{status[0]}: {new_data}", reply_markup=str1_conf)


'''
    Старт/Стоп Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:config:set:"))
async def str1_config_set(callback_query):
    data = callback_query.data.split(":")

    status = callback_query.message.text.split(":")

    figi = data[3]
    user_id = callback_query.from_user.id
    account_id = get_account(user_id=user_id)

    new_data = float(status[1])

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    if status[0] == "Количество лотов":
        cursor.execute("UPDATE str1_config SET quantity_lots=? WHERE user_id = ? AND figi = ? AND account_id = ?",
                       (int(new_data), user_id, figi, account_id))
    elif status[0] == "Тейк-профит(%)":
        cursor.execute("UPDATE str1_config SET take_profit=? WHERE user_id = ? AND figi = ? AND account_id = ?",
                       (new_data / 100, user_id, figi, account_id))
    elif status[0] == "Стоп-лосс(%)":
        cursor.execute("UPDATE str1_config SET stop_loss=? WHERE user_id = ? AND figi = ? AND account_id = ?",
                       (new_data / 100, user_id, figi, account_id))

    connection.commit()

    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"{status[0]} успешно изменено!")
