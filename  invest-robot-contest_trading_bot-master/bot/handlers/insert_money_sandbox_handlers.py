from main import dp
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.add_money_sandbox import add_money_sandbox
from config.personal_data import get_account_type

"""

    Тут представлены все хэндлеры, которые отвечают за добавление денег в песочницу

"""

"""
    Выбор валюты и суммы
"""


@dp.message_handler(state="*", text="Пополнить счёт")
async def add_money_sandbox_start(message: Message):
    if get_account_type(message.from_user.id) == "sandbox":

        choose_sum = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text=f"1000₽", callback_data=f"sandbox:add:1000:rub"),
                    InlineKeyboardButton(text=f"10000₽", callback_data=f"sandbox:add:10000:rub"),
                ],
                [
                    InlineKeyboardButton(text=f"500$", callback_data=f"sandbox:add:500:usd"),
                    InlineKeyboardButton(text=f"5000$", callback_data=f"sandbox:add:5000:usd")
                ],
                [
                    InlineKeyboardButton(text=f"500€", callback_data=f"sandbox:add:500:eur"),
                    InlineKeyboardButton(text=f"5000€", callback_data=f"sandbox:add:5000:eur")
                ],
                [
                    InlineKeyboardButton(text=f"500₺", callback_data=f"sandbox:add:500:try"),
                    InlineKeyboardButton(text=f"5000₺", callback_data=f"sandbox:add:5000:try")
                ],
                [
                    InlineKeyboardButton(text=f"500HK$", callback_data=f"sandbox:add:500:hkd"),
                    InlineKeyboardButton(text=f"5000HK$", callback_data=f"sandbox:add:5000:hkd")
                ],
                [
                    InlineKeyboardButton(text=f"500¥", callback_data=f"sandbox:add:500:jpy"),
                    InlineKeyboardButton(text=f"5000¥", callback_data=f"sandbox:add:5000:jpy")
                ],
                [
                    InlineKeyboardButton(text=f"500₣", callback_data=f"sandbox:add:500:chf"),
                    InlineKeyboardButton(text=f"5000₣", callback_data=f"sandbox:add:5000:chf")
                ],
                [
                    InlineKeyboardButton(text=f"500£", callback_data=f"sandbox:add:500:gbp"),
                    InlineKeyboardButton(text=f"5000£", callback_data=f"sandbox:add:5000:gbp")
                ],
            ]
        )

        await message.answer("Выберите сумму пополнения:", reply_markup=choose_sum)
    else:
        await message.answer("Пополнение возможно только для песочницы!")


"""
    Второй хэндлер, который пополняет счёт
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("sandbox:add"))
async def add_money_sandbox_finish(callback_query):
    data = callback_query.data.split(":")

    sum = data[2]
    currency = data[3]

    add_money_sandbox(user_id=callback_query.from_user.id, sum=sum, currency=currency)
