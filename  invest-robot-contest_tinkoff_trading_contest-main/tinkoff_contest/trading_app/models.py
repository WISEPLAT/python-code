from django.db import models
from knowledge_base.models import Strategy

import trading_app.services.choices as choices

# Create your models here.


class TradingBot(models.Model):

    id = models.AutoField(primary_key=True)
    process_id = models.CharField(max_length=20)
    name = models.CharField(max_length=150)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)


class Trade(models.Model):

    bot = models.ForeignKey(TradingBot, on_delete=models.CASCADE)
    stock = models.CharField(max_length=15)
    timestamp = models.DateTimeField()
    order_type = models.CharField(max_length=50, choices=choices.ORDER_TYPES,
                                  default=choices._ORDER_TYPE_UNSPECIFIED)
    direction = models.CharField(max_length=50, choices=choices.DIRECTION_TYPES,
                                 default=choices._DIRECTION_TYPE_UNSPECIFIED)
    quantity = models.FloatField()
    price = models.FloatField()
    account_id = models.CharField(max_length=20)
    order_id = models.CharField(max_length=50)



