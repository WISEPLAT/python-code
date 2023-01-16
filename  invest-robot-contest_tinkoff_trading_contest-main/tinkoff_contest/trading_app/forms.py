from django import forms
from services.choices import DIRECTION_TYPES, ORDER_TYPES


class FastDealForm(forms.Form):

    stock = forms.CharField(max_length=15, label='Ценная бумага(Symbol/Ticker)')
    quantity = forms.FloatField(label='Количество лотов')
    price = forms.FloatField(label='Цена 1 лота')
    direction = forms.ChoiceField(choices=DIRECTION_TYPES, label='Купить/Продать')
    order_type = forms.ChoiceField(choices=ORDER_TYPES, label='Маркет/Лимит')
