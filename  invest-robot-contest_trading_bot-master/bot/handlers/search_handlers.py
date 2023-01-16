from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.get_securities import get_security_list
from trading.place_order import buy_order
from trading.trade_help import get_price_figi, get_currency_sing
from config.personal_data import get_account_access

"""

    Тут представлены все хэндлеры, которые отвечают за поиск бумаг

"""

"""
    Создаём состояние ожидания названия
"""


class SearchSFB(StatesGroup):
    wait_sfb = State()


"""
    Хэндлер, который запускает состояние поиска
"""


@dp.message_handler(text="Поиск")
async def search_start(callback_query):
    await bot.send_message(chat_id=callback_query.from_user.id, text="Введите название бумаги или FIGI:")
    await SearchSFB.wait_sfb.set()


"""
    Ждём название или FIGI и выводим информацию по бумаге
"""


@dp.message_handler(state=SearchSFB.wait_sfb)
async def search_finish(message: Message, state: FSMContext):
    security_list = get_security_list(user_id=message.from_user.id, name=message.text)
    if len(security_list) != 0:
        for security in security_list:

            choose_share_keyboard = InlineKeyboardMarkup()
            choose_share_keyboard.add(
                InlineKeyboardButton(text=f"Анализ",
                                     callback_data=f"str1:stat:show:{message.from_user.id}:{security.figi}"))
            if get_account_access(user_id=message.from_user.id) == 1:
                choose_share_keyboard.add(
                    InlineKeyboardButton(text=f"Купить 1 лот", callback_data=f"sfb:buy_now:{security.figi}"))

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


"""

    Бумаги

"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('sfb:buy_now:'))
async def search_buy_now(callback_query):
    data = callback_query.data.split(":")
    figi = data[2]

    order = buy_order(figi=figi, user_id=callback_query.from_user.id, quantity_lots=1, price=0.0, via="bot")

    if order:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"Покупка успешно выполнена!")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Ошибка! Вероятно, у Вас мало средств на счёте!")

