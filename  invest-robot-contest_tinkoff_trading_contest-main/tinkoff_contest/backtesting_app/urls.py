from django.urls import path

from . import views

urlpatterns = [
    path('', views.Backtest.as_view(), name='backtest'),
    path('<int:pk>', views.BacktestConfig.as_view(), name='backtest_config')
]