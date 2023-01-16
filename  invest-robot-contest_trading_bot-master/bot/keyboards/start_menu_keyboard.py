from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config.personal_data import get_account_type
"""
    Клавиатура стартового меню
"""


def get_start_menu(user_id):
    if get_account_type(user_id=user_id) == "sandbox":
        start_menu = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Пополнить счёт"),
                ],
                [
                    KeyboardButton(text="Баланс"),
                    KeyboardButton(text="Бумаги"),
                ],
                [
                    KeyboardButton(text="Статистика"),
                    KeyboardButton(text="Операции"),
                    KeyboardButton(text="Поиск"),

                ],
                [
                    KeyboardButton(text="Открытые ордера"),
                ],
                [
                    KeyboardButton(text="Торговые стратегии"),
                ],
                [
                    KeyboardButton(text="Продать"),
                    KeyboardButton(text="Купить"),
                ],
                [
                    KeyboardButton(text="Изменить Токен"),
                    KeyboardButton(text="Изменить Аккаунт"),
                ],
                [
                    KeyboardButton(text="Удалить все торговые стратегии"),
                ],
            ],
            resize_keyboard=True
        )
    else:
        start_menu = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Открыть песочницу"),
                    KeyboardButton(text="Закрыть песочницу"),

                ],
                [
                    KeyboardButton(text="Баланс"),
                    KeyboardButton(text="Бумаги"),
                ],
                [
                    KeyboardButton(text="Статистика"),
                    KeyboardButton(text="Операции"),
                    KeyboardButton(text="Поиск"),
                ],
                [
                    KeyboardButton(text="Открытые ордера"),
                ],
                [
                    KeyboardButton(text="Торговые стратегии"),
                ],
                [
                    KeyboardButton(text="Продать"),
                    KeyboardButton(text="Купить"),
                ],
                [
                    KeyboardButton(text="Изменить Токен"),
                    KeyboardButton(text="Изменить Аккаунт"),
                ],
                [
                    KeyboardButton(text="Удалить все торговые стратегии"),
                ],

            ],
            resize_keyboard=True
        )
    return start_menu
