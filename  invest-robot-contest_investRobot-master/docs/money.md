# Модуль money

Содержит класс `Money`, используемый для точного хранения роботом денежных типов данных. Устроен аналогично
классам `Quotation` и `MoneyValue` в [Tinkoff Invest API](https://tinkoff.github.io/investAPI/faq_custom_types/#quotation),
вдобавок в нем реализованы методы преобразования в/из int, float, Quotation, MoneyValue, а также операторы сложения,
вычитания, умножения на число

## Money

### Методы

#### __init__
*Входные данные*:

| Field | Type                                 | Description                                                 |
|-------|--------------------------------------|-------------------------------------------------------------|
| value | int / float / Quotation / MoneyValue | Значение                                                    |
| nano  | Optional[int]                        | Значение nano (при использовании необходимо value типа int) |

*Выходные данные*: Money.

#### to_float
Преобразовывает значение в float.

#### to_quotation
Преобразовывает значение в Quotation.

#### to_money_value
Преобразовывает значение в MoneyValue.

*Входные данные*:

| Field    | Type | Description                                     |
|----------|------|-------------------------------------------------|
| currency | str  | Валюта, в которой необходимо вернуть MoneyValue |

*Выходные данные*: MoneyValue.


### Примеры использования

```python
from tinkoff.invest import Quotation
from robotlib.money import Money
q = Quotation(units=1600, nano=250000000)
money_1 = Money(57.25)
money_2 = Money(1000)

money = Money(q) + money_1 + money_2
print(money)
# output: <Money units=2657 nano=500000000>
```