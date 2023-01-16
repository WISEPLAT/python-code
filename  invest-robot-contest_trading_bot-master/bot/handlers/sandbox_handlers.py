from main import dp, bot
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
from tinkoff.invest import Client
from config.personal_data import get_token

"""

    Тут представлены все хэндлеры, которые отвечают за создание или закрытие песочницы

"""

"""
    Открытие песочницы
"""


@dp.message_handler(state="*", text="Открыть песочницу")
async def create_sandbox(message: Message):
    with Client(get_token(message.from_user.id)) as client:
        acc = client.sandbox.get_sandbox_accounts().accounts
        if len(acc) == 0:
            client.sandbox.open_sandbox_account()
            await message.answer("Аккаунт песочницы успешно создан!")
        else:
            await message.answer("У Вас уже есть аккаунт в песочнице!",
                                 reply_markup=get_start_menu(user_id=message.from_user.id))


"""
    Закрытие песочницы
    Выводит список всех аккаунтов
"""


@dp.message_handler(state="*", text="Закрыть песочницу")
async def delete_sandbox_start(message: Message):
    with Client(get_token(message.from_user.id)) as client:
        acc = client.sandbox.get_sandbox_accounts().accounts

        if len(acc) == 0:
            await message.answer("У Вас ещё нет аккаунта в песочнице!:",
                                 reply_markup=get_start_menu(user_id=message.from_user.id))
        else:
            delete_sandbox = InlineKeyboardMarkup()
            for i in acc:
                delete_sandbox.add(InlineKeyboardButton(text=f"{i.id}", callback_data=f"sandbox:close:{i.id}"))

            await message.answer("Выберите аккаунт:",
                                 reply_markup=delete_sandbox)


"""
    Закрытие аккаунта
    Принимает id песочницы и закрывает её
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('sandbox:close'))
async def close_sandbox_finish(callback_query):
    data = callback_query.data.split(":")

    account_id = data[2]

    with Client(get_token(callback_query.from_user.id)) as client:
        client.sandbox.close_sandbox_account(account_id=account_id)
        connection = sl.connect("db/BotDB.db")
        cursor = connection.cursor()

        cursor.execute('DELETE FROM str1_config WHERE user_id=? AND account_id = ?',
                       (callback_query.from_user.id, account_id))

        connection.commit()

    with Client(get_token(callback_query.from_user.id)) as client:
        acc = client.sandbox.get_sandbox_accounts().accounts

        if len(acc) == 0:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id, text="Все аккаунты закрыты!")
        else:
            delete_sandbox = InlineKeyboardMarkup()
            for i in acc:
                delete_sandbox.add(InlineKeyboardButton(text=f"{i.id}", callback_data=f"sandbox:close:{i.id}"))

            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id, text="Выберите аккаунт:",
                                        reply_markup=delete_sandbox)
