# Модуль stats

Содержит классы для ведения статистики торгового робота.

## TradeStatisticsAnalyzer

Основной класс, используемый для записи, хранения и получения статистики, а также генерации отчетов и коротких сводок.

Класс предоставляет возможность преобразовать формат отчета, а также сгенерировать короткую сводку. Для этого необходимо
реализовать классы, унаследованные от `TradeStatisticsProcessorBase` и `TradeStatisticsCalculatorBase` соответственно
и передать объекты этих классов в параметры функции `get_report`. Подробнее см. [примеры использования](#_2).

### Методы

#### __init__
*Входные данные*:

| Field           | Type                      | Description                                                 |
|-----------------|---------------------------|-------------------------------------------------------------|
| positions       | int                       | Значение                                                    |
| money           | float                     | Значение nano (при использовании необходимо value типа int) |
| instrument_info | tinkoff.invest.Instrument | Информация об инструменте тоговли                           |
| logger          | logging.Logger            | Логгер                                                      |

*Выходные данные*: `TradeStatisticsAnalyzer`.


#### add_trade
Запись операции в статистику. Этот метод в основном используется роботом, **не рекомендуется** вызывать его самостоятельно.

*Входные данные*:

| Field | Type                      | Description |
|-------|---------------------------|-------------|
| trade | tinkoff.invest.OrderState | Операция    |


#### cancel_order
Отмена операции, удаление из статистики. Этот метод в основном используется роботом, **не рекомендуется** вызывать его самостоятельно.

*Входные данные*:

| Field    | Type | Description |
|----------|------|-------------|
| order_id | int  | ID операции |

#### get_positions
Получение количества ценных бумаг на счету на текущий момент.

*Выходные данные*: `int`, количество бумаг.

#### get_money
Получение баланса на текущий момент.

*Выходные данные*: `float`, баланс.

#### get_pending_orders
Получение списка нереализованных торговых заявок.

*Выходные данные*: `list[tinkoff.invest.OrderState]`, список заявок.

#### save_to_file
Сохранение статистики в файл.

*Входные данные*:

| Field    | Type | Description    |
|----------|------|----------------|
| filename | str  | Название файла |

#### load_from_file
Чтение статистики из файла.

*Входные данные*:

| Field    | Type | Description    |
|----------|------|----------------|
| filename | str  | Название файла |

*Выходные данные*: `TradeStatisticsAnalyzer`

#### add_backtest_trade
Запись в статистику операции из бэктеста.

*Входные данные*:

| Field     | Type                          | Description        |
|-----------|-------------------------------|--------------------|
| quantity  | int                           | Количество лотов   |
| price     | Quotation                     | Цена лота          |
| direction | tinkoff.invest.OrderDirection | Направление сделки |


#### get_report
Получение отчета о статистике.

Метод собирает датафрейм с полной статистикой об операциях, после чего последовательно
запускает на нем пользовательские обработчики. Для получения краткого отчета запускаются пользовательские генераторы
краткой сводки, и их результаты объединяются в один dict.

*Входные данные*:

| Field       | Type                                | Description               |
|-------------|-------------------------------------|---------------------------|
| processors  | list[TradeStatisticsProcessorBase]  | Обработчики статистики    |
| calculators | list[TradeStatisticsCalculatorBase] | Генераторы краткой сводки |

*Выходные данные*: `dict[str, any], pandas.DataFrame`: словарь с краткой сводкой, полная статистика по операциям.

### Примеры использования

#### Генерация отчета
```python
import pandas as pd
from robotlib.stats import TradeStatisticsAnalyzer, TradeStatisticsProcessorBase, TradeStatisticsCalculatorBase

class BalanceProcessor(TradeStatisticsProcessorBase):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df['balance'] = -(df['total_order_amount'] * df['sign']).cumsum()
        df['instrument_balance'] = (df['lots_executed'] * df['sign']).cumsum()
        return df

    
class BalanceCalculator(TradeStatisticsCalculatorBase):
    def calculate(self, df: pd.DataFrame) -> dict[str, any]:
        final_balance = df['balance'][len(df) - 1]
        final_instrument_balance = df['instrument_balance'][len(df) - 1]
        final_price = df['average_position_price'][len(df) - 1]
        return {
            'final_balance': final_balance,
            'max_loss': -df['balance'].min(),
            'final_instrument_balance': final_instrument_balance,
            'income': final_balance + final_instrument_balance * final_price  # todo: * instrument_info.lot
        }

    
stats: TradeStatisticsAnalyzer
# предположим, что эта статистика уже содержит данные

short_summary, full_report = stats.get_report(processors=[BalanceProcessor()], calculators=[BalanceCalculator()])

print(short_summary)
# output: {'final_balance': -1764.8, 'max_loss': 1889.2, 'final_instrument_balance': 1, 'income': -177.39999999999986}
print(full_report)
# output: dataframe with all the trades
```

## TradeStatisticsProcessorBase

Интерфейс, который необходимо реализовать при необходимости преобразования отчета.

### Методы

#### process

Преобразования отчета

*Входные данные*:

| Field | Type             | Description  |
|-------|------------------|--------------|
| df    | pandas.DataFrame | Полный отчет |

*Выходные данные*: `pandas.DataFrame`: преобразованный отчет.

## TradeStatisticsCalculatorBase

Интерфейс, который необходимо реализовать для преобразования краткой сводки.

### Методы

#### calculate

*Входные данные*:

| Field | Type             | Description  |
|-------|------------------|--------------|
| df    | pandas.DataFrame | Полный отчет |

*Выходные данные*: `dict[str, any]`: словарь ключ-значение, содержащий краткую сводку.