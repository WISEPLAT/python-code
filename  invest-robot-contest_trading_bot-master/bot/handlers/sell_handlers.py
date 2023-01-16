from main import dp, bot
from trading.get_account_info import get_lots_portfolio
from tinkoff.invest import Client
from trading.trade_help import is_in_portfolio, get_price_figi
from config.personal_data import get_account, get_token
from trading.place_order import sell_sfb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.get_account_info import get_currency_sing, get_price_in_portfolio
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram import types
from trading.trade_help import in_lot_figi
from trading.get_securities import security_name_by_figi
from trading.check_av import check_time
from config.personal_data import get_account_type, get_account_access
from trading.trade_help import quotation_to_float
from trading.trade_help import get_currency_sing

"""

    Тут представлены все хэндлеры, которые отвечают за продажу бумаг

"""

"""
    Создаём три состояния FSM
"""


class SellOrder(StatesGroup):
    s_wait_figi = State()
    s_wait_quantity = State()
    s_wait_price = State()


"""
    Первый хэндлер, который запускает состояние продажи
"""


@dp.message_handler(text="Продать")
async def start_sell(message):
    if get_account_access(message.from_user.id) == 1:

        empty_portfolio = True

        user_id = message.from_user.id

        with Client(get_token(message.from_user.id)) as client:

            if get_account_type(message.from_user.id) == "sandbox":
                portfolio = client.sandbox.get_sandbox_portfolio(account_id=get_account(message.from_user.id))
            else:
                portfolio = client.operations.get_portfolio(account_id=get_account(message.from_user.id))

            for i in portfolio.positions:
                if i.instrument_type != "currency":
                    empty_portfolio = False

                    sell_keyboard = InlineKeyboardMarkup()
                    sell_keyboard.add(InlineKeyboardButton(text=f"Продать", callback_data=f"sell:figi:{i.figi}"))

                    if i.instrument_type == "share":
                        inst = "Акции"
                    elif i.instrument_type == "bond":
                        inst = "Бонды"
                    elif i.instrument_type == "future":
                        inst = "Фьючерсы"
                    elif i.instrument_type == "etf":
                        inst = "ETF"
                    else:
                        inst = i.instrument_type

                    if get_account_type(message.from_user.id) == "sandbox":
                        text = f"🧾<b>{inst} {security_name_by_figi(figi=i.figi, user_id=user_id)}</b>\n"\
                        f"FIGI: {i.figi}\n\n"\
                        f"Лотов в портфеле: {int(quotation_to_float(i.quantity_lots))}\n"\
                        f"Бумаг в лоте: {in_lot_figi(figi=i.figi, user_id=user_id)}\n\n"\
                        f"Средняя цена бумаги: {round(quotation_to_float(i.average_position_price), 4)}{get_currency_sing(i.average_position_price.currency)}\n"\
                        f"Средняя цена лота: {round(quotation_to_float(i.average_position_price)*in_lot_figi(figi=i.figi, user_id=user_id), 4)}{get_currency_sing(i.average_position_price.currency)}\n\n"\
                        f"Итого стоимость: {round(quotation_to_float(i.average_position_price)*quotation_to_float(i.quantity), 4)}{get_currency_sing(i.average_position_price.currency)}\n "
                    else:
                        text = f"🧾<b>{inst} {security_name_by_figi(figi=i.figi, user_id=user_id)}</b>\n"\
                        f"FIGI: {i.figi}\n\n"\
                        f"Лотов в портфеле: {int(quotation_to_float(i.quantity_lots))}\n"\
                        f"Бумаг в лоте: {in_lot_figi(figi=i.figi, user_id=user_id)}\n\n"\
                        f"Цена бумаги: {round(quotation_to_float(i.current_price), 4)}{get_currency_sing(i.current_price.currency)}\n"\
                        f"Средняя цена лота: {round(quotation_to_float(i.current_price)*in_lot_figi(figi=i.figi, user_id=user_id), 4)}{get_currency_sing(i.average_position_price.currency)}\n\n"\
                        f"Итого стоимость: {round(quotation_to_float(i.current_price)*quotation_to_float(i.quantity), 4)}{get_currency_sing(i.average_position_price.currency)}\n"

                    await bot.send_message(chat_id=user_id, text=text,reply_markup=sell_keyboard)

        if empty_portfolio:
            await bot.send_message(chat_id=user_id, text=f"<b>У Вас нет бумаг!</b>")
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"<b>У Вас используется токен только для чтения!</b>")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("sell:figi"))
async def s_choose_quantity(callback_query, state: FSMContext):
    data = callback_query.data.split(":")
    figi = data[2]

    # Проверяем, есть ли такая акция в портфеле
    if is_in_portfolio(figi, user_id=callback_query.from_user.id):
        if check_time(user_id=callback_query.from_user.id, figi=figi)[0] or get_account_type(
                user_id=callback_query.from_user.id) == "sandbox":

            lot_keyboard = ReplyKeyboardMarkup()
            av_lots = get_lots_portfolio(figi=figi, user_id=callback_query.from_user.id)
            for i in range(av_lots):
                lot_keyboard.add(f"{i + 1}")
                if i == 6:
                    break
            lot_keyboard.add(f"Отмена")

            # Включим клавиатуру
            await bot.send_message(chat_id=callback_query.from_user.id, text=f"Доступно лотов: {av_lots}\nУкажите "
                                                                             f"количество лотов для продажи:",
                                   reply_markup=lot_keyboard)

            # Запишем данные о FIGI в память
            await state.update_data(s_chosen_figi=figi)

            # Перейдём в следующее состояние
            await SellOrder.s_wait_quantity.set()
            return

        else:
            await state.reset_state()
            await bot.send_message(chat_id=callback_query.from_user.id, text="Торги ещё не начались!")
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=check_time(user_id=callback_query.from_user.id, figi=callback_query.text)[1],
                                   reply_markup=get_start_menu(callback_query.from_user.id))

    # В случае ошибки повторим запрос
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Такой бумаги нет в портфеле!")
        return


"""
    Третий хендлер, который исполняется в состоянии s_wait_quantity
"""


@dp.message_handler(state=SellOrder.s_wait_quantity)
async def s_choose_price(message: Message, state: FSMContext):
    # Получим цену бумаги
    try:
        int(message.text)
    except:
        await message.answer("Вы ввели неверный формат!")
    else:
        user_data = await state.get_data()
        price = get_price_in_portfolio(user_data['s_chosen_figi'], user_id=message.from_user.id)

        # Проверяем, есть ли такое количество лотов в портфеле
        if get_lots_portfolio(user_data['s_chosen_figi'], user_id=message.from_user.id) >= int(message.text) > 0:

            # Запишем данные о количестве в память
            await state.update_data(s_chosen_quantity=message.text)

            # Создаём клавиатуру с ценами
            # Для удобства было добавлено несколько цен на 1% и 2% меньше/больше текущей
            # При этом также можно ввести свою цену
            price_keyboard = ReplyKeyboardMarkup()

            price_keyboard.add(f"Лучшая цена")
            price_keyboard.add(f"{round(price * 1.02, 5)}")
            price_keyboard.add(f"{round(price * 1.01, 5)}")
            price_keyboard.add(f"{round(price * 1.00, 6)}")
            price_keyboard.add(f"{round(price * 0.99, 5)}")
            price_keyboard.add(f"{round(price * 0.98, 5)}")
            price_keyboard.add(f"Отмена")

            # Включаем клавиатуру
            await message.answer(f"Укажите цену за бумагу (или напишите свою):",
                                 reply_markup=price_keyboard)

            # Переходим в следующее состояние
            await SellOrder.s_wait_price.set()
            return

        # В случае ошибки повторяем запрос
        else:
            await message.answer(f"Введите доступное число лотов!")
            return


"""
    Последний хендлер, который исполняется в состоянии s_wait_price
"""


@dp.message_handler(state=SellOrder.s_wait_price)
async def s_finish(message: types.Message, state: FSMContext):
    # Получаем цену бумаги

    if message.text == "Лучшая цена":

        user_data = await state.get_data()

        # Продаём бумаги и выводим сообщение об этом

        await state.finish()

        order = sell_sfb(figi=user_data['s_chosen_figi'], price=0.0,
                         quantity_lots=int(user_data['s_chosen_quantity']), user_id=message.from_user.id, via="bot")

        if order:
            await message.answer(
                f"Продажа ценных бумаг {security_name_by_figi(order.figi, message.from_user.id)} в количестве {order.lots_requested} лотов по цене {quotation_to_float(order.initial_order_price)}{get_currency_sing(order.initial_order_price.currency)}.\n",
                reply_markup=get_start_menu(message.from_user.id))
        else:
            await message.answer("Ошибка!")

    else:
        try:
            float(message.text)
        except:
            await message.answer("Вы ввели неверный формат!")
        else:
            user_data = await state.get_data()
            price = get_price_in_portfolio(user_data['s_chosen_figi'], user_id=message.from_user.id)

            # Проверяем, что цена находится в разумных пределах

            if (price * 1.20) > float(message.text) > (price * 0.80):
                # Продаём бумаги и выводим сообщение об этом

                await state.finish()

                order = sell_sfb(figi=user_data['s_chosen_figi'], price=float(message.text),
                                 quantity_lots=int(user_data['s_chosen_quantity']), user_id=message.from_user.id,
                                 via="bot")

                if order:
                    await message.answer(
                        f"Выставлен ордер на продажу ценных бумаг {security_name_by_figi(order.figi,message.from_user.id)} в количестве {order.lots_requested} лотов по цене {quotation_to_float(order.initial_order_price)}{get_currency_sing(order.initial_order_price.currency)}.\n",
                        reply_markup=get_start_menu(message.from_user.id))
                else:
                    await message.answer("Ошибка!")


            # В случае ошибки повторяем запрос
            else:
                await message.answer(f"Введите корректную стоимость!")
                return
