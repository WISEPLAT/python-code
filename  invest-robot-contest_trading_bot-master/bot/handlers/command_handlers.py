from main import dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram import types
import sqlite3 as sl
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


'''
    Выводит приветственный текст при вводе команды /start
    Добавляет новых пользователей в базу
'''


@dp.message_handler(commands="start")
async def start_command(message: Message):

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    info = cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,))
    if info.fetchone() is None:
        user = (
            message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username,
            "none",
            "none", "none", "none", "new")
        cursor.execute("INSERT INTO users (user_id, first_name, last_name, username, token, account_id, account_type, "
                       "account_access, bot_access_level) VALUES(?, ?, ?, ?, ?, ?, ?, ?,?);", user)
        connection.commit()

    await message.answer("Добро пожаловать в торговый бот!", reply_markup=get_start_menu(message.from_user.id))

    get_token_keyboard = InlineKeyboardMarkup()
    get_token_keyboard.add(InlineKeyboardButton(text="Выпустить токен", url="https://www.tinkoff.ru/invest/settings"
                                                                            "/api/"))

    await message.answer("Чтобы торговать с помощью бота необходимо выпустить Токен Invest API.\n\n"
                         "Для его выпуска можно перейти по ссылке ниже или самостоятельно зайти на сайт Тинькофф -> "
                         "Инвестиции -> Найстройки -> Создать токен (в самом низу).\n "
                         "\n<b>Типы Токенов</b>\n\n"
                         "<b>Только для чтения</b>: возможно просматривать баланс, состояние портфеля.\n"
                         "<b>Полный доступ</b>: возможно торговать бумагами.", reply_markup=get_token_keyboard)
    await message.answer("Также бот позволяет торговать в песочнице")


'''
    Отменяет текущее состояние / возвращает в главное меню
'''


@dp.message_handler(state="*", commands="cancel")
async def cancel_command(message: types.Message, state: FSMContext):
    await message.answer("Действие было отменено!", reply_markup=get_start_menu(message.from_user.id))
    await state.reset_state()


@dp.message_handler(state="*", text="Отмена")
async def cancel_command_text(message: types.Message, state: FSMContext):
    await message.answer("Действие было отменено!", reply_markup=get_start_menu(message.from_user.id))
    await state.reset_state()


'''
    Выводит приветственный текст при вводе текста
'''


@dp.message_handler(commands="hello")
async def hello_command(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Это торговый бот. Пока я мало что умею, но я хороший!")


'''
    Выводит текст помощи
'''


@dp.message_handler(commands="help")
async def help_command(message: Message):
    await message.answer(f"Короче тут пока ничего нет)")
