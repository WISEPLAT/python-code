from main import dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
import sqlite3 as sl
from tinkoff.invest import Client
from config.crypto_rsa import encrypt

"""

    Тут представлены все хэндлеры, которые отвечают за добавление токена

"""

"""
    Создаём состояние ожидания
"""


class TokenWaiting(StatesGroup):
    wait_token = State()


"""
    Первый хэндлер, который запускает состояние ожидания
"""


@dp.message_handler(state="*", text="Изменить Токен")
async def choose_token_start(message: Message):
    await message.answer("Внимание! При изменении токена все торговые стратегии будут удалены!")
    await message.answer("Введите токен!", reply_markup=ReplyKeyboardRemove())
    await TokenWaiting.next()


"""
    Второй хэндлер, который исполняется в состоянии s_wait_figi
"""


@dp.message_handler(state=TokenWaiting.wait_token, content_types=types.ContentTypes.TEXT)
async def choose_token_finish(message: Message, state: FSMContext):
    token = message.text
    try:
        with Client(token) as client:

            acc = client.users.get_accounts()

            connection = sl.connect("db/BotDB.db")
            cursor = connection.cursor()

            encrypted_token = encrypt(token)
            account_id = acc.accounts[0].id
            account_type = acc.accounts[0].type
            account_access = acc.accounts[0].access_level

            cursor.execute('UPDATE users SET token = ?, account_id = ?, account_type = ?, account_access = ? WHERE '
                           'user_id = ?;',
                           (sl.Binary(encrypted_token), account_id, account_type, account_access,
                            message.from_user.id))

            cursor.execute('DELETE FROM str1_config WHERE user_id = ?;',
                           (message.from_user.id,))

            connection.commit()

            await message.answer("Ваш токен добавлен!", reply_markup=get_start_menu(message.from_user.id))
            await message.delete()
            await state.finish()

    except:
        await message.answer("Такого токена не существует! Введите снова!")
        return
