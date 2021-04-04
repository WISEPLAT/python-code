import pyowm
import telebot
from pyowm.utils.config import get_default_config

config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = pyowm.OWM('52c6e3564a536747b8bfbac88626e58a', config_dict)
bot = telebot.TeleBot("1724773764:AAGXz0u-Anc-2c7TuAlo2ayScfVX_bgox3o", parse_mode=None)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(message.text)
    w = observation.weather
    #print(w.wind()['speed'], w.temperature('celsius')['temp'])
    weather_info = "В городе "+message.text+" сейчас "+w.detailed_status+"\n"
    weather_info += "Температура: " + str(w.temperature('celsius')['temp']) + "\n"
    weather_info += "Скорость ветра: " + str(w.wind()['speed']) + " м/с" + "\n"

    bot.reply_to(message, weather_info)


bot.polling()
