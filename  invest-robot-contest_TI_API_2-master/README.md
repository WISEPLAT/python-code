# TI_API_2
>Example of trade analysis tool and robot on python with Tinkoff API
Пример аналитического инструмента торговли и (в будущем) торгового робота. Этот инструмент проработки торговых стратегий через Tinkoff API работает из сейчас только при непосредственном взаимодействии с файлами на языке python.


### Для работы с файлами нужно заполнить:
1. [intro/basek.py](https://github.com/khutdi/TI_API_2/blob/master/intro/basek.py) добавив туда свой **токен** <br/>
2. Затем с помощью [Account_n_Portfolio.py](https://github.com/khutdi/TI_API_2/blob/master/Account_n_Portfolio.py) можно получить **ID аккаунта** <br/>
3. Его нужно для дальнейшей работы добавить в файл [intro/accid.py](https://github.com/khutdi/TI_API_2/blob/master/intro/accid.py) <br/>

### Доступные сейчас возможности:

- Скачивание списка фьючерсов и акций через [Get_Futures_Shares_List.py](https://github.com/khutdi/TI_API_2/blob/master/Get_Futures_Shares_List.py)
- Скачивание исторических данных "свечей" выбранного инструмента (по figi) через [Instr_last_candles.py]([Instr_last_candles.py](https://github.com/khutdi/TI_API_2/blob/master/I)nstr_last_candles.py)
- Тестирование на исторических данных стратегии MA cross EMA (Получим данные в виде таблицы) через [History_check.py (сейчас настроенное на фьючерсы)](https://github.com/khutdi/TI_API_2/blob/master/History_check.py)
- Построение графика данных для проверки полученных результатов используя Matplotlib через [History_check.py](https://github.com/khutdi/TI_API_2/blob/master/History_check.py) тот же файл, разкомментированием строк 127-134
