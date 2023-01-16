from main import bot, dp
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram import types
from config.personal_data import ADMIN_ID
import asyncio
import aioschedule
from trading.strategy.str1 import start_str1

'''
    Тут описаны все хэндлеры с основными командами бота
'''

'''
    Отправляет сообщение администратору (мне), что бот запущен
'''


async def start(dp):
    #await bot.send_message(chat_id=ADMIN_ID, text="Бот запущен", reply_markup=get_start_menu(ADMIN_ID))
    await set_default_commands(dp)
    asyncio.create_task(schedule_ema_adx_macd())


'''
    Устанавливаем команды меню
'''


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("cancel", "Отмена"),
        types.BotCommand("hello", "Приветствие"),
    ])


'''
    Запускаем автоматический анализ графиков
'''


async def schedule_ema_adx_macd():
    aioschedule.every(15).minutes.do(start_str1)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)



