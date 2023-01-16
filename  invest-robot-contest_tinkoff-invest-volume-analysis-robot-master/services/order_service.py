import csv
import logging
import threading
from datetime import datetime
from itertools import groupby
from os.path import exists
from typing import List

from tinkoff.invest import Client, OrderType, OrderDirection

from constants import APP_NAME
from domains.order import Order
from services.telegram_service import TelegramService
from settings import NOTIFICATION, ACCOUNT_ID, TOKEN, IS_SANDBOX, CAN_REVERSE_ORDER
from utils.exchange_util import is_open_orders
from utils.format_util import fixed_float
from utils.instrument_util import get_instrument_by_name
from utils.order_util import is_order_already_open, get_reverse_order

logger = logging.getLogger(__name__)

orders_file_path = "./../data/orders.csv"


def write_file(order: Order):
    try:
        order_dict = dict(order)
        with open(orders_file_path, "a", newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(order_dict.keys())
            writer.writerow(order_dict.values())
    except Exception as ex:
        logger.error(ex)


def rewrite_file(orders: List[Order]):
    try:
        with open(orders_file_path, "w", newline='') as file:
            writer = csv.writer(file)
            for order in orders:
                order_dict = dict(order)
                if file.tell() == 0:
                    writer.writerow(order_dict.keys())
                writer.writerow(order_dict.values())
    except Exception as ex:
        logger.error(ex)


def load_orders():
    orders: List[Order] = []

    if not exists(orders_file_path):
        return orders

    try:
        with open(orders_file_path, newline='') as file:
            reader = csv.DictReader(file)
            # header = next(reader)
            for row in reader:
                order = Order.from_dict(row)
                if order.status == "open":
                    # после запуска приложения анализирую только незакрытые позиции
                    orders.append(order)
    except Exception as ex:
        logger.error(ex)

    return orders


def open_order(
        figi: str,
        quantity: int,
        direction: OrderDirection,
        order_id: str,
        order_type: OrderType = OrderType.ORDER_TYPE_MARKET
):
    if not ACCOUNT_ID:
        logger.error("Не задан счет для торговли. Проверьте общие настройки приложения")

    with Client(TOKEN, app_name=APP_NAME) as client:
        try:
            # todo может возникнуть ситуация, когда будет создано 100 позиций с 1 лотом в каждой
            #  сервер не позволит выполнить моментально 100 запросов
            if IS_SANDBOX:
                close_order = client.sandbox.post_sandbox_order(
                    account_id=ACCOUNT_ID,
                    figi=figi,
                    quantity=quantity,
                    direction=direction,
                    order_type=order_type,
                    order_id=order_id
                )
            else:
                close_order = client.orders.post_order(
                    account_id=ACCOUNT_ID,
                    figi=figi,
                    quantity=quantity,
                    direction=direction,
                    order_type=order_type,
                    order_id=order_id
                )
            logger.info(close_order)
            return close_order
        except Exception as ex:
            logger.error(ex)


# в отдельном потоке, чтобы не замедлял процесс обработки
class OrderService(threading.Thread):
    def __init__(self, is_notification=False, can_open_orders=False):
        super().__init__()

        self.telegram_service = TelegramService(NOTIFICATION["bot_token"], NOTIFICATION["chat_id"])

        self.is_notification = is_notification
        self.can_open_orders = can_open_orders
        self.orders: List[Order] = load_orders()

    def create_order(self, order: Order):
        try:
            if order is None:
                return

            if is_order_already_open(self.orders, order):
                logger.info(f"сделка в направлении {order.direction} уже открыта: {order}")
                return

            if CAN_REVERSE_ORDER:
                active_orders = get_reverse_order(self.orders, order)
                if len(active_orders) > 0:
                    # если поступила сделка в обратном направлении, то переворачиваю позицию
                    logger.info(f"переворачиваю позицию - поступила сделка в обратном направлении: {order}")
                    for active_order in active_orders:
                        # цена закрытия предыдущей сделки = цене открытия новой
                        self.close_order(active_order, order.open)

            instrument = get_instrument_by_name(order.instrument)
            if self.can_open_orders:
                new_order = open_order(
                    figi=instrument["future"],
                    quantity=order.quantity,
                    direction=order.direction,
                    order_id=order.id
                )
                order.order_id = new_order.order_id

            self.orders.append(order)
            write_file(order)

            logger.info(f"✅ ТВ {order.instrument}: цена {order.open}, тейк {order.take}, стоп {order.stop}")
            if self.is_notification:
                self.telegram_service.post(
                    f"✅ ТВ {order.instrument}: цена {order.open}, тейк {order.take}, стоп {order.stop}")
        except Exception as ex:
            logger.error(ex)

    def close_order(self, order: Order, close_price: float):
        order.status = "close"
        order.close = close_price
        if order.direction == OrderDirection.ORDER_DIRECTION_BUY.value:
            order.result = order.close - order.open
            order.is_win = order.result > 0
        else:
            order.result = order.open - order.close
            order.is_win = order.result > 0

        if order.is_win:
            logger.info(f"закрыта заявка по тейк-профиту с результатом {order.result}; открыта в {order.time}")
        else:
            logger.info(f"закрыта заявка по стоп-лоссу с результатом {order.result}; открыта в {order.time}")

        if self.can_open_orders:
            instrument = get_instrument_by_name(order.instrument)
            # закрываю сделку обратным ордером
            reverse_direction = OrderDirection.ORDER_DIRECTION_BUY.value
            if order.direction == OrderDirection.ORDER_DIRECTION_BUY.value:
                reverse_direction = OrderDirection.ORDER_DIRECTION_SELL.value

            open_order(
                figi=instrument["future"],
                quantity=order.quantity,
                direction=reverse_direction,
                order_id=f"{order.id}-close"
            )

        # перезаписываю файл с результатами сделок
        # todo перенести хранение сделок в БД
        rewrite_file(self.orders)
        if self.is_notification:
            self.telegram_service.post(f"закрыта позиция на {order.instrument}: результат {order.result}")

    def processed_orders(self, instrument: str, current_price: float, time: datetime):
        for order in self.orders:
            if order.status == "active":
                if not is_open_orders(time):
                    # закрытие сделок по причине приближении закрытии биржи
                    self.close_order(order, current_price)
                    continue

                if order.instrument != instrument:
                    continue

                if order.direction == OrderDirection.ORDER_DIRECTION_BUY.value:
                    if current_price < order.stop:
                        # закрываю активные buy-заявки по стопу, если цена ниже стоп-лосса
                        self.close_order(order, current_price)
                    elif current_price > order.take:
                        # закрываю активные buy-заявки по цели, если цена выше заданной цели
                        self.close_order(order, current_price)
                else:
                    if current_price > order.stop:
                        # закрываю активные sell-заявки по стопу, если цена выше стоп-лосса
                        self.close_order(order, current_price)
                    elif current_price < order.take:
                        # закрываю активные sell-заявки по цели, если цена ниже заданной цели
                        self.close_order(order, current_price)

    def write_statistics(self):
        groups = groupby(self.orders, lambda order: order.instrument)
        for instrument, group in groups:
            file_path = f"./../logs/statistics-{instrument}.log"
            orders: List[Order] = list(group)
            with open(file_path, "a", encoding="utf-8") as file:
                take_orders = list(filter(lambda x: x.is_win, orders))
                earned_points = sum(order.result for order in take_orders)
                loss_orders = list(filter(lambda x: not x.is_win, orders))
                lost_points = sum(order.result for order in loss_orders)
                total = earned_points + lost_points

                logger.info(f"инструмент: {instrument}")
                logger.info(f"количество сделок: {len(orders)}")
                logger.info(f"успешных сделок: {len(take_orders)}")
                logger.info(f"заработано пунктов: {fixed_float(earned_points)}")
                logger.info(f"отрицательных сделок: {len(loss_orders)}")
                logger.info(f"потеряно пунктов: {fixed_float(lost_points)}")
                logger.info(f"итого пунктов: {fixed_float(total)}")
                logger.info("-------------------------------------")

                file.write(f"количество сделок: {len(orders)}\n")
                file.write(f"успешных сделок: {len(take_orders)}\n")
                file.write(f"заработано пунктов: {fixed_float(earned_points)}\n")
                file.write(f"отрицательных сделок: {len(loss_orders)}\n")
                file.write(f"потеряно пунктов: {fixed_float(lost_points)}\n\n")
                file.write(f"итого пунктов: {fixed_float(total)}\n")
                file.write("-------------------------------------\n")
