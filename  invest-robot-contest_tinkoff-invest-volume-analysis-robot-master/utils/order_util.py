from datetime import datetime
from typing import List
from uuid import uuid4

from tinkoff.invest import OrderDirection

from domains.order import Order


# подготовка списка ордеров для открытия сделки
def prepare_orders(
        instrument: str,
        current_price: float,
        time: datetime,
        stop_loss: float,
        direction: OrderDirection,
        count_lots: int,
        count_goals: int,
        goal_step: float,
        first_goal: int
) -> List[Order]:
    group_id = str(uuid4())
    quantity = int(count_lots / count_goals)

    orders = []
    step = 1
    final_step = (goal_step * count_goals) + 1
    while step < final_step:
        take = current_price - ((stop_loss - current_price) * first_goal * step)
        order = Order(
            id=str(uuid4()),
            group_id=group_id,
            instrument=instrument,
            open=current_price,
            stop=stop_loss,
            take=take,
            quantity=quantity,
            direction=direction.value,
            time=time
        )
        orders.append(order)
        step += goal_step
    return orders


def is_order_already_open(orders: List[Order], order: Order) -> bool:
    active_order = list(filter(
        lambda item: item.instrument == order.instrument and
                     item.direction == order.direction and
                     item.status == "active",
        orders)
    )
    if len(active_order) > 0:
        # если уже есть активная заявка, но она с одной группы (точки входа), то считаю ее новой
        if order.group_id == active_order[0].group_id:
            return False
        # если уже есть активная заявка, но она не совпадает с текущей группой (точкой входа),
        # то запрещаю создание новой до тех пор, пока активная заявка не будет закрыта
        return True
    return False


# возвращаю текущие открытые сделки, если поступила новая с обратным направлением
def get_reverse_order(orders: List[Order], order: Order) -> List[Order]:
    active_order = list(filter(
        lambda item: item.instrument == order.instrument and
                     item.status == "active" and
                     item.direction != order.direction,
        orders)
    )
    return active_order
