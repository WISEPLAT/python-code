from main import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.get_account_info import get_currency_sing
from main import dp
from aiogram.types import Message, ReplyKeyboardMarkup
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from trading.trade_help import in_lot_figi, get_price_figi, quotation_to_float
from trading.place_order import buy_order
from trading.check_av import check_time
from config.personal_data import get_account_type, get_account_access, get_account
from trading.get_securities import get_security_list
from trading.get_securities import security_name_by_figi
"""

    Тут представлены все хэндлеры, которые отвечают за продажу бумаг

"""

"""
    Создаём три состояния FSM
"""


class SearchSecurityBuy(StatesGroup):
    wait_sfb_buy = State()


class BuyOrder(StatesGroup):
    b_wait_figi = State()
    b_wait_quantity = State()
    b_wait_price = State()


"""
    Начало поиска бумаг
"""


@dp.message_handler(text="Купить")
async def start_buy(message):
    if get_account_access(message.from_user.id) == 1:
        await bot.send_message(chat_id=message.from_user.id, text="Введите название бумаги или FIGI:")
        await SearchSecurityBuy.wait_sfb_buy.set()
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"<b>У Вас используется токен только для чтения!</b>")


"""
    Поиск бумаг на покупку
"""


@dp.message_handler(state=SearchSecurityBuy.wait_sfb_buy)
async def search_security_buy(message: Message, state: FSMContext):
    security_list = get_security_list(user_id=message.from_user.id, name=message.text)
    if len(security_list) != 0:
        for security in security_list:

            choose_share_keyboard = InlineKeyboardMarkup()
            choose_share_keyboard.add(
                InlineKeyboardButton(text=f"Купить", callback_data=f"buy:figi:{security.figi}"))

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
    Выбор количества лотов
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("buy:figi"))
async def b_choose_quantity(callback_query, state: FSMContext):
    data = callback_query.data.split(":")
    figi = data[2]

    # Проверяем, доступна ли она сейчас для покупки
    if check_time(user_id=callback_query.from_user.id, figi=figi)[0] or get_account_type(
            user_id=callback_query.from_user.id) == "sandbox":

        # Запишем в память
        await state.update_data(b_chosen_figi=figi)

        # Создаём клавиатуру с примерами лотов
        lot_keyboard = ReplyKeyboardMarkup()
        lot_keyboard.add(f"1")
        lot_keyboard.add(f"2")
        lot_keyboard.add(f"3")
        lot_keyboard.add(f"4")
        lot_keyboard.add(f"Отмена")

        await bot.send_message(chat_id=callback_query.from_user.id, text="Укажите количество лотов для покупки:",
                               reply_markup=lot_keyboard)

        # Перейдём в следующее состояние
        await BuyOrder.b_wait_quantity.set()
        return
    else:
        await state.reset_state()
        await bot.send_message(chat_id=callback_query.from_user.id, text="Торги ещё не начались!")
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=check_time(user_id=callback_query.from_user.id, figi=figi)[1],
                               reply_markup=get_start_menu(callback_query.from_user.id))


"""
    Третий хэндлер, который находится в состоянии b_wait_quantity
"""


@dp.message_handler(state=BuyOrder.b_wait_quantity)
async def b_choose_price(message: Message, state: FSMContext):
    # Проверяем корректность введённых данных
    try:
        int(message.text)
    except:
        await message.answer("Вы ввели неверный формат!")
    else:
        if int(message.text) > 0:

            # Запишем в память
            await state.update_data(b_chosen_quantity=message.text)

            user_data = await state.get_data()
            price = get_price_figi(user_data['b_chosen_figi'], user_id=message.from_user.id)

            # Создадим клавиатуру с примерами цены на бумагу
            price_keyboard = ReplyKeyboardMarkup()

            price_keyboard.add(f"Лучшая цена")
            price_keyboard.add(f"{round(price * 1.02, 5)}")
            price_keyboard.add(f"{round(price * 1.01, 5)}")
            price_keyboard.add(f"{round(price * 1.00, 5)}")
            price_keyboard.add(f"{round(price * 0.99, 5)}")
            price_keyboard.add(f"{round(price * 0.98, 5)}")
            price_keyboard.add(f"Отмена")

            # Включим клавиатуру
            await message.answer("Укажите цену за бумагу:", reply_markup=price_keyboard)
            await BuyOrder.b_wait_price.set()

        # В случае ошибки повторим запрос
        else:
            await message.answer("Введите корректное число лотов!")


"""
    Последний хэндлер, который покупает бумаги
"""


@dp.message_handler(state=BuyOrder.b_wait_price)
async def b_finish(message: types.Message, state: FSMContext):
    if message.text == "Лучшая цена":

        user_data = await state.get_data()

        await state.finish()

        # Продадим бумаги и выведем сообщение

        order = buy_order(figi=user_data['b_chosen_figi'], price=0.0,
                          quantity_lots=int(user_data['b_chosen_quantity']), user_id=message.from_user.id, via="bot")

        if order:
            await message.answer(
                f"Покупка ценных бумаг {security_name_by_figi(order.figi, message.from_user.id)} в количестве {order.lots_requested} лотов по цене {quotation_to_float(order.initial_order_price)}{get_currency_sing(order.initial_order_price.currency)}.\n",
                reply_markup=get_start_menu(message.from_user.id))
        else:
            await message.answer("Ошибка! Вероятно, у Вас мало средств на счёте!")
    else:

        try:
            float(message.text)
        except:
            await message.answer("Вы ввели неверный формат!")
        else:
            user_data = await state.get_data()
            price = get_price_figi(user_data['b_chosen_figi'], user_id=message.from_user.id)

            # Проверяем, что цена находится в разумных границах

            if price * 1.20 > float(message.text) > price * 0.80:
                await state.finish()

                order = buy_order(figi=user_data['b_chosen_figi'], price=float(message.text),
                                  quantity_lots=int(user_data['b_chosen_quantity']), user_id=message.from_user.id,
                                  via="bot")
                if order:
                    await message.answer(
                        f"Выставлен ордер на покупку ценных бумаг {security_name_by_figi(order.figi,message.from_user.id)} в количестве {order.lots_requested} лотов по цене {quotation_to_float(order.initial_order_price)}{get_currency_sing(order.initial_order_price.currency)}.\n",
                        reply_markup=get_start_menu(message.from_user.id))
                else:
                    await message.answer("Ошибка! Вероятно, у Вас мало средств на счёте!")

            # В случае ошибки повторим запрос
            else:
                await message.answer("Введите корректную цену!")
                return
