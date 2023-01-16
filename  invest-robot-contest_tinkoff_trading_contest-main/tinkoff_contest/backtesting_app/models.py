from django.db import models
from knowledge_base.models import Strategy

# Create your models here.


class StrategyConfig(models.Model):
    """
    Configuration model for strategies, contains json config of parameters
    """
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    configuration = models.JSONField(default=dict({'Empty':'Empty'}), blank=True)

    def __str__(self):
        return self.strategy.name

    class Meta:
        verbose_name = 'Конфигурация'
        verbose_name_plural = 'Конфигурации'


class BacktestResult(models.Model):
    """
    Backtest result
    """
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    stock = models.CharField(max_length=50)
    timeframe = models.CharField(max_length=5)
    config = models.JSONField(default=dict({'Empty':'Empty'}), blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    number_of_trades = models.IntegerField()
    winning_trades = models.FloatField()
    profit = models.FloatField()

    def __str__(self):
        return '_'.join([self.strategy.name, self.stock, self.timeframe,
                         str(self.start_date.year), str(self.start_date.month), str(self.start_date.day),
                         str(self.end_date.year), str(self.end_date.month), str(self.end_date.day),
                         ])

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'


