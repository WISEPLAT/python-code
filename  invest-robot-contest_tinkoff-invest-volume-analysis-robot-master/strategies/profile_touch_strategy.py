import datetime
import logging
import threading
from typing import List, Optional

import pandas as pd
from tinkoff.invest import TradeDirection, OrderDirection

from constants import FIVE_MINUTES_TO_SECONDS
from domains.order import Order
from utils.exchange_util import is_open_orders, is_premarket_time
from visualizers.finplot_graph import FinplotGraph
from settings import PROFILE_PERIOD, FIRST_TOUCH_VOLUME_LEVEL, SECOND_TOUCH_VOLUME_LEVEL, FIRST_GOAL, \
    PERCENTAGE_STOP_LOSS, SIGNAL_CLUSTER_PERIOD, IS_SHOW_CHART, GOAL_STEP, COUNT_LOTS, COUNT_GOALS
from utils.order_util import prepare_orders
from utils.strategy_util import is_price_in_range_cluster, ticks_to_cluster, calculate_ratio, \
    processed_volume_levels_to_times, apply_frame_type

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.width = None

logger = logging.getLogger(__name__)


# стратегия касание объемного уровня
class ProfileTouchStrategy(threading.Thread):
    def __init__(self, instrument_name):
        super().__init__()

        self.instrument_name = instrument_name

        self.df = pd.DataFrame(columns=["figi", "direction", "price", "quantity", "time"])
        self.df = apply_frame_type(self.df)

        self.first_tick_time = None
        self.fix_date = {}
        self.clusters = None
        self.processed_volume_levels = {}

        if IS_SHOW_CHART:
            self.visualizer = FinplotGraph(SIGNAL_CLUSTER_PERIOD)
            self.visualizer.start()

    def set_df(self, df: pd.DataFrame):
        self.df = df
        logger.info("загружен новый DataFrame")

    def analyze(
            self,
            trade_df: pd.DataFrame
    ) -> Optional[List[Order]]:
        trade_data = trade_df.iloc[0]
        current_price = trade_data["price"]
        time = trade_data["time"]

        if is_premarket_time(time):
            return

        if PROFILE_PERIOD not in self.fix_date:
            self.fix_date[PROFILE_PERIOD] = time.hour

        if self.first_tick_time is None:
            # сбрасываю секунды, чтобы сравнивать "целые" минутные свечи
            self.first_tick_time = time.replace(second=0, microsecond=0)

        if self.fix_date[PROFILE_PERIOD] < time.hour:
            # построение кластерных свечей и графика раз в 1 час
            self.fix_date[PROFILE_PERIOD] = time.hour
            self.calculate_clusters()

        self.df = pd.concat([self.df, trade_df])

        if self.clusters is not None:
            for index, cluster in self.clusters.iterrows():
                cluster_time = cluster["time"]
                cluster_price = cluster["max_volume_price"]

                # цена может коснуться объемного уровня в заданном процентном диапазоне
                is_price_in_range = is_price_in_range_cluster(current_price, cluster_price)
                if is_price_in_range:
                    timedelta = time - cluster_time
                    if timedelta < datetime.timedelta(minutes=FIRST_TOUCH_VOLUME_LEVEL):
                        continue

                    if cluster_price not in self.processed_volume_levels:
                        # инициализация первого касания уровня
                        self.processed_volume_levels[cluster_price] = {}
                        self.processed_volume_levels[cluster_price]["count_touches"] = 0
                        self.processed_volume_levels[cluster_price]["times"] = {}
                    else:
                        # обработка второго и последующего касания уровня на основе времени последнего касания
                        if self.processed_volume_levels[cluster_price]["last_touch_time"] is not None:
                            timedelta = time - self.processed_volume_levels[cluster_price]["last_touch_time"]
                            if timedelta < datetime.timedelta(minutes=SECOND_TOUCH_VOLUME_LEVEL):
                                continue

                    # установка параметров при касании уровня
                    self.processed_volume_levels[cluster_price]["count_touches"] += 1
                    self.processed_volume_levels[cluster_price]["last_touch_time"] = time
                    self.processed_volume_levels[cluster_price]["times"][time] = None

                    count_touches = self.processed_volume_levels[cluster_price]['count_touches']
                    logger.info("объемный уровень %s сформирован %s", cluster_price, cluster_time)
                    logger.info("время %s: цена %s подошла к объемному уровню %s раз\n", time, current_price, count_touches)
                    break

        if (time - self.first_tick_time).total_seconds() >= FIVE_MINUTES_TO_SECONDS:
            # сбрасываю секунды, чтобы сравнивать завершенные свечи
            self.first_tick_time = time.replace(second=0, microsecond=0)
            # если торги доступны, то каждую завершенную минуту проверяю кластера на возможную ТВ
            if is_open_orders(time) and len(self.processed_volume_levels) > 0:
                return self.check_entry_points(current_price, time)

    def calculate_clusters(self):
        if self.df.empty:
            return
        self.clusters = ticks_to_cluster(self.df, period=PROFILE_PERIOD)
        valid_entry_points, invalid_entry_points = processed_volume_levels_to_times(
            self.processed_volume_levels)
        if IS_SHOW_CHART:
            self.visualizer.render(self.df,
                                   valid_entry_points=valid_entry_points,
                                   invalid_entry_points=invalid_entry_points,
                                   clusters=self.clusters)

    def check_entry_points(
            self,
            current_price: float,
            time: datetime
    ) -> Optional[List[Order]]:
        for volume_price, volume_level in self.processed_volume_levels.items():
            for touch_time, value in volume_level["times"].items():
                if value is not None:
                    continue
                candles = ticks_to_cluster(self.df, period=SIGNAL_CLUSTER_PERIOD)
                candles = calculate_ratio(candles)
                prev_candle = candles.iloc[-3]
                current_candle = candles.iloc[-2]
                if current_candle.empty or prev_candle.empty:
                    logger.error("свеча не найдена")
                    continue

                if current_candle["win"] is True:
                    # если свеча является сигнальной, то осуществляю сделку
                    max_volume_price = current_candle["max_volume_price"]
                    percent = (max_volume_price * PERCENTAGE_STOP_LOSS / 100)
                    self.processed_volume_levels[volume_price]["times"][touch_time] = True

                    if current_candle["direction"] == TradeDirection.TRADE_DIRECTION_BUY:
                        if prev_candle["open"] < current_candle["open"]:
                            logger.info("пропуск входа - предыдущая свеча открылась ниже текущей")
                            return

                        # todo условие дает плохое соотношение
                        # если подошли к объемному уровню снизу вверх на лонговой свече, то пропускаю вход
                        # if current_candle['close'] < volume_price:
                        #     logger.info(f"пропуск входа - цена закрытия ниже объемного уровня, time={time}, price={current_price}")
                        #     return

                        if current_price < max_volume_price:
                            logger.info(
                                "пропуск входа - цена открытия ниже макс объема в сигнальной свече, время %s, цена %s",
                                time,
                                current_price
                            )
                            return

                        stop = max_volume_price - percent
                        orders = self.prepare_orders(
                            current_price=current_price,
                            time=time,
                            stop=stop,
                            direction=OrderDirection.ORDER_DIRECTION_BUY
                        )
                        logger.info("подтверждена точка входа в лонг, ордера: %s", orders)
                        return orders

                    else:
                        if prev_candle["open"] > current_candle["open"]:
                            logger.info("пропуск входа - предыдущая свеча открылась выше текущей")
                            return

                        # todo условие дает плохое соотношение
                        # если подошли к объемному уровню сверху вниз на шортовой свече, то пропускаю вход
                        # if current_candle['close'] > volume_price:
                        #     logger.info(f"пропуск входа - цена закрытия выше объемного уровня, time={time}, price={current_price}")
                        #     return

                        if current_price > max_volume_price:
                            logger.info(
                                "пропуск входа - цена открытия выше макс объема в сигнальной свече, время %s, цена %s",
                                time,
                                current_price
                            )
                            return

                        stop = max_volume_price + percent
                        orders = self.prepare_orders(
                            current_price=current_price,
                            time=time,
                            stop=stop,
                            direction=OrderDirection.ORDER_DIRECTION_SELL
                        )
                        logger.info("подтверждена точка входа в шорт, ордера: %s", orders)
                        return orders

                else:
                    # если текущая свеча не сигнальная, то ожидаю следующую для возможного входа
                    self.processed_volume_levels[volume_price]["times"][touch_time] = False
                    self.processed_volume_levels[volume_price]["last_touch_time"] = None

    def prepare_orders(
            self,
            current_price: float,
            time: datetime,
            stop: float,
            direction: OrderDirection
    ) -> List[Order]:
        return prepare_orders(
            instrument=self.instrument_name,
            current_price=current_price,
            time=time,
            stop_loss=stop,
            direction=direction,
            count_lots=COUNT_LOTS,
            count_goals=COUNT_GOALS,
            goal_step=GOAL_STEP,
            first_goal=FIRST_GOAL
        )
