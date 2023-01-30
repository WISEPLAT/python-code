# region общие настройки робота
# токен профиля для Тинькофф Инвестиций
# инструкция https://tinkoff.github.io/investAPI/token/
TOKEN = ""

# режим работы: песочница или реальный счет
IS_SANDBOX = True

# счет для торговли в зависимости от выбранного режима работы
ACCOUNT_ID = ""

# массив анализируемых инструментов
INSTRUMENTS = [
    {"name": "USD000UTSTOM", "alias": "USD/RUB", "figi": "BBG0013HGFT4", "future": "BBG00VHGV1J0"},
    {"name": "SBER", "figi": "BBG004730N88", "future": "FUTSBRF06220"},
    {"name": "GAZP", "figi": "BBG004730RP0", "future": "FUTGAZR06220"},
]

# приложение выступает в роли советника или робота с открытием позиций
CAN_OPEN_ORDERS = True

# признак переворачивания позиции, если определена ТВ в противоположное направление
CAN_REVERSE_ORDER = True

# количество лотов на 1 точку входа
COUNT_LOTS = 2

# количество целей на 1 точку входа
COUNT_GOALS = 2

# соотношение к стоп-лоссу: если стоп 5пункта, то первая цель будет 5*3=15пунктов
FIRST_GOAL = 3

# размер шага для очередной цели
# если лотов 2, то будет открыто 2 сделки:
# цель для 1ой будет рассчитан по значению FIRST_GOAL
# цель для 2ой будет увеличен на указанный шаг
GOAL_STEP = 0.5

# процент от макс объема в сигнальной свече, на который устанавливается стоп-лосс
# стоп устанавливается ниже/выше макс объема в свече
PERCENTAGE_STOP_LOSS = 0.03

# отображение графика при анализе
IS_SHOW_CHART = False

# отправка уведомлений в чат телеграм
NOTIFICATION = {
    "bot_token": "",
    "chat_id": ""
}
# endregion общие настройки робота

# region настройки стратегии
# период профиля рынка, примеры: 1min, 1h, 1d, 1m
PROFILE_PERIOD = "1h"

# ТФ сигнальной свечи для рассмотрения ТВ, примеры: 1min, 1h, 1d, 1m
SIGNAL_CLUSTER_PERIOD = "5min"

# время в минутах, через которое можем рассматривать первое касание объемного уровня
FIRST_TOUCH_VOLUME_LEVEL = 90

# время в минутах для последующих касаний объемного уровня
SECOND_TOUCH_VOLUME_LEVEL = 5

# процент, на который цена может превысить или не дойти до объемного уровня
PERCENTAGE_VOLUME_LEVEL_RANGE = 0.03
# endregion настройки стратегии