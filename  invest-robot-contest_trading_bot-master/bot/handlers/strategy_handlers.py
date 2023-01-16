from main import dp
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import sqlite3 as sl
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext


'''
    Выводит варианты алготрейдинга
'''


@dp.message_handler(text="Торговые стратегии")
async def algo_trade(message: Message):
    await message.answer(f"Выберите торговую стратегию:\n")

    str1_keyboard = InlineKeyboardMarkup()
    str1_keyboard.add(InlineKeyboardButton(text="Торговля", callback_data="str1:list"))
    str1_keyboard.add(
        InlineKeyboardButton(text="Добавить бумагу в стратегию", callback_data="str1:settings:add:start"))
    str1_keyboard.add(
        InlineKeyboardButton(text="Удалить бумагу из стратегии", callback_data="str1:settings:delete:start"))

    await message.answer(f"EMA + ADX + MACD\n", reply_markup=str1_keyboard)


class DeleteStrategy(StatesGroup):
    wait_yes_or_no = State()


@dp.message_handler(Text(contains="Удалить все торговые стратегии", ignore_case=True))
async def delete_all_strategies_start(message: Message):
    text = ""

    connection = sl.connect("db/BotDB.db")
    cursor = connection.cursor()

    strategies = cursor.execute('SELECT account_id, account_type, name FROM str1_config WHERE user_id = ?', (message.from_user.id,))

    for line in strategies:
        text += f"ID аккаунта: {line[0]}\n"
        if line[1] == "sandbox":
            text += f"Песочница\n"
        elif line[1] == "1":
            text += f"Брокерский счёт\n"
        text += f"Бумаги {line[2]}\n\n"

    if text:
        await message.answer(f"Все открытые стратегии стратегии:\n")
        await message.answer(text)
        await DeleteStrategy.wait_yes_or_no.set()

        await message.answer(
            f"Напишите <b>ДА</b> для удаления всех торговых стратегий.\n\nНапишите <b>НЕТ</b> для отмены.",
            reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer("У Вас нет открытых стратегий!")


@dp.message_handler(state=DeleteStrategy.wait_yes_or_no)
async def delete_all_strategies_finish(message: Message, state: FSMContext):

    if message.text.upper() == "ДА":
        connection = sl.connect("db/BotDB.db")
        cursor = connection.cursor()

        cursor.execute('DELETE FROM str1_config WHERE user_id = ?',
                                    (message.from_user.id,))

        connection.commit()

        await state.reset_state()

        await message.answer("Все стратегии были удалены!", reply_markup=get_start_menu(message.from_user.id))

    elif message.text.upper() == "НЕТ":

        await state.reset_state()

        await message.answer("Операция отменена!", reply_markup=get_start_menu(message.from_user.id))

    else:
        await message.answer("Введите <b>ДА</b> или <b>НЕТ</b>!")


