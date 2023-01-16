from main import dp, bot
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
from tinkoff.invest import Client
from config.personal_data import get_token

"""

    Тут представлены все хэндлеры, которые отвечают за добавление аккаунта

"""

"""
    Выводит список всех аккаунтов
"""


@dp.message_handler(state="*", text="Изменить Аккаунт")
async def choose_account(message: Message):
    token = get_token(message.from_user.id)

    choose_account = InlineKeyboardMarkup()
    with Client(str(token)) as client:
        acc = client.users.get_accounts()
        acc_sand = client.sandbox.get_sandbox_accounts()
        for i in acc.accounts:
            if i.type == 1:
                choose_account.add(InlineKeyboardButton(text=f"{i.name}", callback_data=f"account:{i.id}:{i.type}:{i.access_level}"))
        for i in acc_sand.accounts:
            choose_account.add(InlineKeyboardButton(text=f"Песочница", callback_data=f"account:{i.id}:sandbox:{i.access_level}"))

    await message.answer("Внимание! Не забудьте остановить торговые стратегии (в случае необходимости) перед сменой "
                         "аккаунта!")
    await message.answer("Выберите аккаунт:", reply_markup=choose_account)


"""
    Второй хэндлер, который исполняется в состоянии s_wait_figi
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("account"))
async def account_finish(callback_query):
    data = callback_query.data.split(":")

    account_id = data[1]
    account_type = data[2]
    account_access = data[3]

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()
    cursor.execute('UPDATE users SET account_id = ?, account_type = ?, account_access = ? WHERE user_id = ?;',
                      (str(account_id), str(account_type), str(account_access), callback_query.from_user.id))
    connection.commit()

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Аккаунт успешно изменён!",
                           reply_markup=get_start_menu(user_id=callback_query.from_user.id))
