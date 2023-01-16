from django.shortcuts import render, redirect
from django.views import View
import json

from .forms import StrategyForm, BacktestStockForm
from .models import StrategyConfig

# Create your views here.


class Backtest(View):

    @staticmethod
    def get(request):
        context = {
            'Strategies': 1,
            'StrategyForm': StrategyForm(),
        }

        return render(request, "backtesting_app/choose_strat.html", context)

    @staticmethod
    def post(request):
        return redirect(to='backtest_config', pk=request.POST['strategy'])


class BacktestConfig(View):

    @staticmethod
    def get(request, pk):
        try:
            choosen_config = StrategyConfig.objects.filter(strategy__id=pk)[0].configuration
            context = {
                'config': choosen_config,
                'time': BacktestStockForm(),
                'button': 'Применить',
            }
        except IndexError:
            context = {
                'error': 'Стратегии с таким id не существует',
                'button': 'Назад',
            }

        return render(request, "backtesting_app/strategy_config.html", context)

    @staticmethod
    def post(request, pk):
        if len(request.POST) == 1:
            return redirect(to='backtest')

        return redirect(to='backtest')


