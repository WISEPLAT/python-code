import asyncio
import logging
import os
from contextlib import suppress

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import (BotBlocked, MessageNotModified,
                                      NetworkError)

import my_moving_average
import robot_fatbold

BOT_TOKEN = os.environ["INVEST_BOT_TOKEN"]
password = os.environ["INVEST_BOT_PASSWORD"]
available_passwords = [password]


# Состояния для проверки доступа к боту
class bot_access(StatesGroup):
    waiting_for_password = State()
    waiting_for_start = State()


""" Переключатели для понимания в каком состоянии находится торговый робот
if robot_must_work == False, то при следующем выходе из генератора, цикл
прервется и торговый робот будет отключен.
"""
trade_robot_states = {
    "status_trade_robot": False,
    "robot_must_work": True
}

bot_access.waiting_for_password.set()

# Объект бота
bot = Bot(token=BOT_TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

help = """
/help - показывает подсказку \n
/set - устанавливает настройки \n
Cообщение "Запустить торгового робота" запускает робота с настройками,
которые ты задал или настройками по умолчанию. \n
Cообщение "Остановить торгового робота" останавливает робота
примерно за 60 сек. \n
Cообщение "Настройки" показывает способ задать настройки \n

Робот работает по стратегии: \n
 short_ma > long_ma открывает позицию \n
 short_ma < long_ma продает акции \n


"""

# Список доступных параметров
trade_parametrs = (
    'long_ma',
    'short_ma',
    'std_period',
    'start_balance_units',
    'long_ma_min',
    'long_ma_max',
    'short_ma_min',
    'short_ma_max',
    'std_period_min',
    'std_period_max',
)


# Настройки по умолчанию для боевого робота и песочницы
user_data = {
    'long_ma': 15,
    'short_ma': 3,
    'std_period': 5,
    'start_balance_units': 100000,
    'long_ma_min': 13,
    'long_ma_max': 15,
    'short_ma_min': 3,
    'short_ma_max': 4,
    'std_period_min': 6,
    'std_period_max': 8,
}


def check_access() -> bool:
    if bot_access.waiting_for_password:
        return False


def get_keyboard_fab(parametr: str) -> types.InlineKeyboardMarkup:
    buttons = [
        types.InlineKeyboardButton(
            text="-1",
            callback_data=callback_numbers.new(
                parametr=parametr,
                action="decr")),
        types.InlineKeyboardButton(
            text="+1",
            callback_data=callback_numbers.new(
                parametr=parametr,
                action="incr")),
        types.InlineKeyboardButton(
            text="Подтвердить",
            callback_data=callback_numbers.new(
                parametr=parametr,
                action="finish"))]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


async def update_num_text_fab(message: types.Message,
                              parametr: str, new_value: int):
    with suppress(MessageNotModified):
        await message.edit_text(f"Укажите значение {parametr}: {new_value}",
                                reply_markup=get_keyboard_fab(parametr))


callback_numbers = CallbackData("numbers", "parametr", "action")

callback_sets = CallbackData("sets", "parametr")


@dp.callback_query_handler(callback_sets.filter())
async def callbacks_change_parametr(call: types.CallbackQuery,
                                    callback_data: dict):

    user_value = user_data[callback_data["parametr"]]
    parametr = callback_data["parametr"]

    await update_num_text_fab(call.message, parametr, user_value)

    await call.answer()


@dp.callback_query_handler(callback_numbers.filter(action=["incr", "decr"]))
async def callbacks_num_change(call: types.CallbackQuery, callback_data: dict):

    parametr = callback_data["parametr"]
    user_value = user_data[parametr]

    action = callback_data["action"]

    if action == "incr":
        user_data[parametr] = user_value + 1
        await update_num_text_fab(call.message, parametr, user_value + 1)
    elif action == "decr":
        user_data[parametr] = user_value - 1
        await update_num_text_fab(call.message, parametr, user_value - 1)
    await call.answer()


@dp.callback_query_handler(callback_numbers.filter(action=["finish"]))
async def callbacks_num_finish_fab(call: types.CallbackQuery,
                                   callback_data: dict):

    parametr = callback_data["parametr"]
    user_value = user_data[parametr]
    await call.message.edit_text(f"""Установлено значение {parametr}:
                                     {user_value}""")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):

    await message.answer("Введите пароль")
    await bot_access.waiting_for_password.set()


async def check_password(message):
    if message.text not in available_passwords:
        await message.answer("Пароль неверный! Укажите правильный пароль:")
        return
    await bot_access.waiting_for_start.set()

    """Запускает бота"""
    greeting = """Привет! Я робот. Меня зовут Толстый жирный.\n
               Я умею торговать на бирже.
               И делать твое депо толстым и жирным.\n
               Ты можешь ввести команду /help и прочитать инструкцию
               по работе со мной.\n Она выглядит так:
               """
    await message.answer(greeting)
    await message.answer(help)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "Запустить торгового робота",
        "Тест в песочнице",
        "Настройки",
        "Инструкция",
        "Баланс"
    ]
    keyboard.add(*buttons)
    await message.answer("Что делать, хозяин?", reply_markup=keyboard)


@dp.message_handler(Text(equals="главное меню"))
async def main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "Запустить торгового робота",
        "Тест в песочнице",
        "Настройки",
        "Инструкция",
        "Баланс"
    ]
    keyboard.add(*buttons)
    await message.answer("Что делать, хозяин?", reply_markup=keyboard)


@dp.message_handler(Text(equals="Баланс"))
async def get_balance(message: types.Message):

    # info = await robot_fatbold.get_balance()
    await message.answer("""Пока не работает. Потому, что надо передавать
                            все параметры стратегии, чтобы получить данные
                            """)


@dp.message_handler(commands=password)
async def cmd_password(message: types.Message):
    """Запускает бота"""
    greeting = """Привет! Я робот. Меня зовут Толстый жирный.\n
                  Я умею торговать на бирже.
                  И делать твое депо толстым и жирным.\n
                  Ты можешь ввести команду /help
                  и прочитать инструкцию по работе со мной.\n
                  Она выглядит так:
                  """
    await message.answer(greeting)
    await message.answer(help)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "Запустить торгового робота",
        "Тест в песочнице",
        "Настройки",
        "Инструкция",
        "Баланс"
    ]
    keyboard.add(*buttons)
    await message.answer("Что делать, хозяин?", reply_markup=keyboard)


@dp.message_handler(Text(equals="Запустить торгового робота"))
async def start_trade(message: types.Message):

    # if check_access() == False:
    #     await message.answer("У вас нет доступа к боту. Введите пароль:")
    #     return

    if not trade_robot_states["status_trade_robot"]:

        status = "Working"

        gen = robot_fatbold.main(
            long_ma=user_data["long_ma"],
            short_ma=user_data["short_ma"],
            std_period=user_data["std_period"])

        flag = True  # Чтобы один раз сообщить, что робот запущен.

        while status == "Working" and trade_robot_states["robot_must_work"]:
            response = await gen.__anext__()

            trade_robot_states["status_trade_robot"] = True

            status = response['status']

            await asyncio.sleep(0.1)

            if flag and status == "Working":
                keyboard = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=2)
                buttons = [
                    "Остановить торгового робота",
                    "Тест в песочнице",
                    "Настройки",
                    "Инструкция",
                    "Баланс"
                ]
                keyboard.add(*buttons)
                await message.answer("Торговый робот запущен!",
                                     reply_markup=keyboard)
                flag = False
                trade_robot_states["status_trade_robot"] = True
                trade_robot_states["robot_must_work"] = True

            # status = response['status']
            # Робот работает ничего не делаем

        trade_robot_states["status_trade_robot"] = False  # Изменим статус
        # Поднимим флаг, чтобы робот мог запуститься
        trade_robot_states["robot_must_work"] = True
        balance = response['balance']
        profit = response['profit']
        shares = response['shares']
        send_message = f"""
        Робот остановлен.
        Текущий cтатус: {status} \n
        Сумма на счете: {balance:.2f} \n
        Стоимость акций: {shares:.2f} \n
        Прибыль с момента запуска: {profit:.2f}
        """

        await message.answer(send_message)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            "Запустить торгового робота",
            "Тест в песочнице",
            "Настройки",
            "Инструкция",
            "Баланс"
        ]
        keyboard.add(*buttons)
        await message.answer("Что делать, хозяин?", reply_markup=keyboard)

    elif trade_robot_states["status_trade_robot"]:
        await message.answer("Робот уже запущен")
    else:
        await message.answer("Робот в непонятном состоянии")


@dp.message_handler(lambda message: message.text ==
                    "Остановить торгового робота")
async def stop_trade(message: types.Message):

    if trade_robot_states['status_trade_robot']:
        # Глобальная переменная для остановки робота
        trade_robot_states['robot_must_work'] = False
        await message.answer("Робот будет остановлен в течении ~60 сек.")
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            "Запустить торгового робота",
            "Тест в песочнице",
            "Настройки",
            "Инструкция",
            "Баланс"
        ]
        keyboard.add(*buttons)

        await message.answer("Робот и так не работал", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Тест в песочнице")
async def sandbox_test(message: types.Message):
    send_message = "Запущен тест на песочнице:"
    await message.answer(send_message)

    results = my_moving_average.main(
        user_data['start_balance_units'],
        user_data['long_ma_min'],
        user_data['long_ma_max'],
        user_data['short_ma_min'],
        user_data['short_ma_max'],
        user_data['std_period_min'],
        user_data['std_period_max']
    )

    send_message = "Тест на песочнице закончен:"
    await message.answer(send_message)

    best_settings = results[0]['settings']
    best_result_message = f"""
    Лучшие настройки:
    Прибыль: {float(results[0]['profit']):.2f}
    Инструмент: {best_settings['stock']}
    long_ma: {best_settings['long_ma']}
    short_ma: {best_settings['short_ma']}
    std_period: {best_settings['std_period']}
    tf: {best_settings['tf']}
    period: {best_settings['period']}
    """

    await message.answer(best_result_message)

    send_message = "Остальные результаты:"
    await message.answer(send_message)

    for i in range(1, len(results)):
        settings = results[i]['settings']
        result_message = f"""
        Прибыль: {float(results[i]['profit']):.2f}
        Инструмент: {settings['stock']}
        long_ma: {settings['long_ma']}
        short_ma: {settings['short_ma']}
        std_period: {settings['std_period']}
        tf: {settings['tf']}
        period: {settings['period']}
        """
        await message.answer(result_message)


@dp.message_handler(lambda message: message.text == "Настройки")
async def settings_setup(message: types.Message):

    buttons = []

    for p in trade_parametrs:
        # Получим текущее значение параметра для текста на кнопке
        user_value = user_data[p]
        button_text = p + ":" + str(user_value)
        buttons.append(
            types.InlineKeyboardButton(
                text=button_text,
                callback_data=callback_sets.new(
                    parametr=p)))

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.answer("Выберите параметр:", reply_markup=keyboard)


@dp.message_handler(commands="set")
async def set(message: types.Message):

    global long_ma
    global short_ma
    global std_period

    m_message = message.text.split(sep=";")

    long_ma = m_message[0].split()[1]
    short_ma = m_message[1]
    std_period = m_message[2]

    await message.answer(f"""Установлены настройки робота \n
    long_ma: {long_ma}    \n
    short_ma: {short_ma}     \n
    std_period: {std_period}   \n
    """)


@dp.message_handler(lambda message: message.text == "Инструкция")
async def show_help(message: types.Message):

    await message.answer(help)


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя
    # из БД
    print(
        f"""Меня заблокировал пользователь!\n
            Сообщение: {update}\nОшибка: {exception}
        """)

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True


@dp.errors_handler(exception=NetworkError)
async def error_Network_Error(update: types.Update, exception: NetworkError):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя
    # из БД
    print(
        f"""ClientConnectorError: Cannot connect to host
            api.telegram.org:443 ssl:default [None] \n
            Сообщение: {update}\nОшибка: {exception}
            """)

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True


def register_handlers_access(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(
        check_password,
        state=bot_access.waiting_for_password)
    dp.register_message_handler(main_menu, state=bot_access.waiting_for_start)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
