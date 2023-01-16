from django.contrib import admin
from .models import StrategyConfig, BacktestResult

# Register your models here.

admin.site.register(StrategyConfig)
admin.site.register(BacktestResult)

