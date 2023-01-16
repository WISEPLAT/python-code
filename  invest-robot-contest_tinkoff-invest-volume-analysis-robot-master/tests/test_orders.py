import unittest

from tinkoff.invest import OrderDirection

from utils.order_util import prepare_orders


class TestOrders(unittest.TestCase):
    def test_prepare_buy_two_orders(self):
        actual_orders = prepare_orders(
            instrument="SBER",
            time="2022-05-20 15:13:15.830627+00:00",
            direction=OrderDirection.ORDER_DIRECTION_BUY,
            current_price=100,
            stop_loss=80,
            count_lots=10,
            count_goals=2,
            first_goal=3,
            goal_step=0.5,
        )

        actual_first_order = actual_orders[0]
        self.assertEqual(actual_first_order.instrument, "SBER")
        self.assertEqual(actual_first_order.open, 100)
        self.assertEqual(actual_first_order.close, None)
        self.assertEqual(actual_first_order.stop, 80)
        self.assertEqual(actual_first_order.take, 160)
        self.assertEqual(actual_first_order.quantity, 5)
        self.assertEqual(actual_first_order.direction, 1)
        self.assertEqual(actual_first_order.time, "2022-05-20 15:13:15.830627+00:00")
        self.assertEqual(actual_first_order.status, "active")
        self.assertEqual(actual_first_order.result, None)
        self.assertEqual(actual_first_order.is_win, None)

        actual_second_order = actual_orders[1]
        self.assertEqual(actual_second_order.instrument, "SBER")
        self.assertEqual(actual_second_order.open, 100)
        self.assertEqual(actual_second_order.close, None)
        self.assertEqual(actual_second_order.stop, 80)
        self.assertEqual(actual_second_order.take, 190)
        self.assertEqual(actual_second_order.quantity, 5)
        self.assertEqual(actual_second_order.direction, 1)
        self.assertEqual(actual_second_order.time, "2022-05-20 15:13:15.830627+00:00")
        self.assertEqual(actual_second_order.status, "active")
        self.assertEqual(actual_second_order.result, None)
        self.assertEqual(actual_second_order.is_win, None)

    def test_prepare_sell_three_orders(self):
        actual_orders = prepare_orders(
            instrument="SBER",
            time="2022-05-20 15:13:15.830627+00:00",
            direction=OrderDirection.ORDER_DIRECTION_SELL,
            current_price=100,
            stop_loss=120,
            count_lots=9,
            count_goals=3,
            first_goal=3,
            goal_step=0.5,
        )

        actual_first_order = actual_orders[0]
        self.assertEqual(actual_first_order.instrument, "SBER")
        self.assertEqual(actual_first_order.open, 100)
        self.assertEqual(actual_first_order.close, None)
        self.assertEqual(actual_first_order.stop, 120)
        self.assertEqual(actual_first_order.take, 40)
        self.assertEqual(actual_first_order.quantity, 3)
        self.assertEqual(actual_first_order.direction, 2)
        self.assertEqual(actual_first_order.time, "2022-05-20 15:13:15.830627+00:00")
        self.assertEqual(actual_first_order.status, "active")
        self.assertEqual(actual_first_order.result, None)
        self.assertEqual(actual_first_order.is_win, None)

        actual_second_order = actual_orders[1]
        self.assertEqual(actual_second_order.instrument, "SBER")
        self.assertEqual(actual_second_order.open, 100)
        self.assertEqual(actual_second_order.close, None)
        self.assertEqual(actual_second_order.stop, 120)
        self.assertEqual(actual_second_order.take, 10)
        self.assertEqual(actual_second_order.quantity, 3)
        self.assertEqual(actual_second_order.direction, 2)
        self.assertEqual(actual_second_order.time, "2022-05-20 15:13:15.830627+00:00")
        self.assertEqual(actual_second_order.status, "active")
        self.assertEqual(actual_second_order.result, None)
        self.assertEqual(actual_second_order.is_win, None)

        actual_third_order = actual_orders[2]
        self.assertEqual(actual_third_order.instrument, "SBER")
        self.assertEqual(actual_third_order.open, 100)
        self.assertEqual(actual_third_order.close, None)
        self.assertEqual(actual_third_order.stop, 120)
        self.assertEqual(actual_third_order.take, -20)
        self.assertEqual(actual_third_order.quantity, 3)
        self.assertEqual(actual_third_order.direction, 2)
        self.assertEqual(actual_third_order.time, "2022-05-20 15:13:15.830627+00:00")
        self.assertEqual(actual_third_order.status, "active")
        self.assertEqual(actual_third_order.result, None)
        self.assertEqual(actual_third_order.is_win, None)


if __name__ == "__main__":
    unittest.main()
