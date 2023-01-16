from django.db import models

# Create your models here.


class Strategy(models.Model):
    """
    Strategy description for knowledge base with best backtest results
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    file_name = models.CharField(max_length=100)
    best_stock = models.CharField(max_length=100, blank=True, default='Empty')
    best_profit = models.CharField(max_length=10, blank=True, default='Empty')
    best_config = models.JSONField(default=dict({'Empty':'Empty'}), blank=True)
    #TODO Дописать скрипт для поиска лучшего бэктеста и записи его результатов сюда

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стратегия'
        verbose_name_plural = 'Стратегии'
