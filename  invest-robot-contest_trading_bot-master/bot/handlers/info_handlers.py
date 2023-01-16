from trading.get_account_info import get_all_stat, get_my_order, get_all_currency, get_all_securities, get_my_operations
from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from trading.get_securities import security_name_by_figi
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.place_order import cancel_order
from config.personal_data import get_account_access

"""

    Здесь собраны все хэндлеры, которые отвечают за вывод информации о счёте

"""

"""

    Баланс

"""


@dp.message_handler(Text(contains="баланс", ignore_case=True))
async def get_balance(message: Message):
    currency_df = get_all_currency(message.from_user.id)

    await message.answer(f"💸<b>Доступная валюта</b>💸")

    text = ""

    for i in currency_df.index:

        if currency_df['exchange_rate'][i] != 0.0 and currency_df['exchange_rate'][i] != 1.0:
            text += (
                f"<b>{currency_df['name'][i]}</b>\n"
                f"{round(currency_df['sum'][i], 2)}{currency_df['sign'][i]} <i>({round(currency_df['sum_in_ruble'][i], 2)}₽)</i>\n\n")
        else:
            text += (
                f"<b>{currency_df['name'][i]}</b>\n"
                f"{round(currency_df['sum'][i], 2)}{currency_df['sign'][i]}\n\n")

    if text:
        await message.answer(text=text)
    else:
        await message.answer(text="У Вас нет средств!")


"""

    Бумаги

"""


@dp.message_handler(Text(contains="бумаги", ignore_case=True))
async def get_share(message: Message):
    security_df = get_all_securities(message.from_user.id)

    empty_portfolio = True
    await message.answer(f"💼Ценные бумаги в портфеле💼")

    for i in security_df.index:

        inst = ""

        if security_df['instrument'][i] == "share":
            inst = "Акции"
            empty_portfolio = False

        elif security_df['instrument'][i] == "bond":
            inst = "Бонды"
            empty_portfolio = False

        elif security_df['instrument'][i] == "etf":
            inst = "ETF"
            empty_portfolio = False

        elif security_df['instrument'][i] == "currency":
            continue

        elif security_df['instrument'][i] == "future":
            inst = "Фьючерсы"
            empty_portfolio = False

        if security_df['exp_yield'][i] >= 0:
            exp_yield = f"Ожидаемый доход: {round(security_df['exp_yield'][i], 2)}₽"
        else:
            exp_yield = f"Ожидаемая убыль: {round(security_df['exp_yield'][i], 2)}₽"

        await message.answer(
            f"🧾<b>{inst} {security_df['security_name'][i]}</b>\n"
            f"FIGI: {security_df['figi'][i]}\n\n"
            f"Лотов: {int(security_df['lots'][i])}\n"
            f"Всего: {round(security_df['quantity'][i], 2)}\n\n"
            f"Средняя цена: {security_df['average_price'][i]}{security_df['currency_sign'][i]}\n"
            f"Средняя цена FIFO: {security_df['average_price_fifo'][i]}{security_df['currency_sign'][i]}\n"
            f"Текущая цена: {round(security_df['current_price'][i], 6)}{security_df['currency_sign'][i]}\n\n"
            f"НКД: {security_df['nkd'][i]}{security_df['currency_sign'][i]}\n"
            f"{exp_yield}{security_df['currency_sign'][i]}\n"
        )

    if empty_portfolio:
        await message.answer(f"У Вас нет ценных бумаг в портфеле!")


"""

    Статистика по счёту

"""


@dp.message_handler(Text(contains="статистика", ignore_case=True))
async def get_stat(message: Message):
    await message.answer(f"📈<b>Статистика по счёту</b>📉 ")

    stat = get_all_stat(message.from_user.id)

    # Посчитаем сумму всех бумаг
    sum = stat['sum_total'][0]

    # Переведём доход/убыток из процентов в рубли
    dif = round(sum - (sum / (100 + stat['exp_yield'][0])) * 100, 2)

    if dif >= 0:
        dif_text = f"<b>Прибыль</b>: {dif}₽ ({stat['exp_yield'][0]}%)"
    else:
        dif_text = f"<b>Убыль</b>: {dif}₽ ({stat['exp_yield'][0]}%)"

    await message.answer(
        f"<b>Акции</b> на сумму: {stat['sum_shares'][0]}₽\n"
        f"<b>Бонды</b> на сумму: {stat['sum_bonds'][0]}₽\n"
        f"<b>ETF</b> на сумму: {stat['sum_etf'][0]}₽\n"
        f"<b>Валюта</b> на сумму: {stat['sum_curr'][0]}₽\n"
        f"<b>Фьючерсы</b> на сумму: {stat['sum_fut'][0]}₽\n\n"
        f"<b>Итого</b>: {round(sum, 2)}₽\n"
        f"{dif_text}\n"

    )


'''
    Открытые ордера
'''


@dp.message_handler(Text(contains="ордер", ignore_case=True))
async def get_orders(message: Message):
    order_df = get_my_order(message.from_user.id)

    await message.answer(f"📋Открытые ордера📋")

    no_orders = True

    for i in order_df.index:

        no_orders = False

        cancel_order_keyboard = InlineKeyboardMarkup()
        if get_account_access(user_id=message.from_user.id) == 1:
            cancel_order_keyboard.add(InlineKeyboardButton(text=f"Отменить ордер", callback_data=f"cancel_order:{order_df['order_id'][i]}"))

        if order_df['direction'][i] == 2:
            direction = "Продажа"
        else:
            direction = "Покупка"

        await message.answer(
            f"✅<b>{direction}</b> бумаг {security_name_by_figi(order_df['figi'][i], message.from_user.id)}\n"
            f"Открыт: {order_df['order_date'][i]}\n\n"
            f"ID: {order_df['order_id'][i]}\n\n"
            f"FIGI: {order_df['figi'][i]}\n\n"
            f"Лотов запрошено: {order_df['lots_req'][i]}\n"
            f"Лотов исполнено: {order_df['lots_ex'][i]}\n\n"
            f"Сумма запрошена: {order_df['sum_req'][i]}{order_df['currency_sign'][i]}\n"
            f"Сумма исполнено: {order_df['sum_ex'][i]}{order_df['currency_sign'][i]}\n\n"
            f"Цена одной акции: {round(order_df['price_one'][i], 6)}{order_df['currency_sign'][i]}\n\n"
            f"Комиссия: {round(order_df['commission'][i], 3)}{order_df['currency_sign'][i]}\n"
            f"Комиссия сервиса: {round(order_df['serv_commission'][i], 3)}{order_df['currency_sign'][i]}\n\n"
            f"Итого: {order_df['sum_total'][i]}{order_df['currency_sign'][i]}\n",
            reply_markup=cancel_order_keyboard
        )
    if no_orders:
        await message.answer(text="У Вас нет открытых ордеров!")


'''
    Закрытие ордера по id
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('cancel_order'))
async def close_order(callback_query):
    data = callback_query.data.split(":")
    order_id = data[1]

    await cancel_order(order_id=order_id, user_id=callback_query.from_user.id)

    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text="❌Ордер отменён❌")


'''
    Операции
'''


@dp.message_handler(Text(contains="операции", ignore_case=True))
async def get_operations(message: Message):

    try:
        operations = get_my_operations(user_id=message.from_user.id)
    except:
        await message.answer("Ошибка!")

    else:
        if operations:
            await message.answer(f"Ваши операции:")

            with open(f"img/operations/all_operations_{message.from_user.id}.png", "rb") as operations_img:
                await bot.send_photo(chat_id=message.from_user.id, photo=operations_img)

        else:
            await message.answer(f"У Вас пока не было операций!")
