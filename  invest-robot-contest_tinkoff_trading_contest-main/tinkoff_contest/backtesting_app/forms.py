from knowledge_base.models import Strategy
from django import forms
from backtesting_app.services.choices import INTERVALS


class StrategyForm(forms.Form):
    """
    Form to choose what strategy to use
    """
    strategy = forms.ModelChoiceField(queryset=Strategy.objects.all())


class BacktestStockForm(forms.Form):
    """
    Form for configuring stock, timeframe and period
    """
    stock = forms.CharField(max_length=50, label='Инструмент')
    timeframe = forms.ChoiceField(choices=INTERVALS, label='Интервал')
    start_date = forms.DateTimeField(label='Начало периода')
    end_date = forms.DateTimeField(label='Конец периода')

