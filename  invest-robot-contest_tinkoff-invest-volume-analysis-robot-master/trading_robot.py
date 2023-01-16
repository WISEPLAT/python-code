import asyncio
import logging
from datetime import timedelta

import pandas as pd
from tinkoff.invest import (
    AsyncClient
)
from tinkoff.invest.utils import now

from constants import ONE_HOUR_TO_MINUTES
from services.order_service import OrderService
from services.user_service import UserService
from settings import INSTRUMENTS, CAN_OPEN_ORDERS, TOKEN
from strategies.profile_touch_strategy import ProfileTouchStrategy
from utils.exchange_util import is_open_exchange
from utils.instrument_util import request_iterator, get_file_path_by_instrument
from utils.logger import init_logging
from utils.parse_util import processed_data
from utils.strategy_util import merge_two_frames, create_empty_df

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.width = None

init_logging()
logger = logging.getLogger(__name__)


class TradingRobot:
    def __init__(self):
        self.order_service = OrderService(is_notification=True, can_open_orders=CAN_OPEN_ORDERS)
        self.order_service.start()

        self.is_history_processed = True

        self.df_by_instrument = {}
        self.strategy = {}
        for instrument in INSTRUMENTS:
            figi = instrument["figi"]
            df_by_instrument = create_empty_df()
            self.df_by_instrument[figi] = df_by_instrument

            file_path = get_file_path_by_instrument(instrument)
            instrument_file = open(file_path, "a", newline='')
            df_by_instrument.to_csv(instrument_file, mode="a", header=instrument_file.tell() == 0, index=False)

            profile_touch_strategy = ProfileTouchStrategy(instrument["name"])
            profile_touch_strategy.start()
            self.strategy[figi] = profile_touch_strategy

    # актуализация DataFrame из полученных ранее данных
    async def sync_df(self, client):
        self.is_history_processed = True
        for instrument in INSTRUMENTS:
            try:
                figi = instrument["figi"]

                file_path = get_file_path_by_instrument(instrument)
                self.df_by_instrument[figi] = pd.read_csv(file_path, sep=",")
                self.df_by_instrument[figi]["time"] = pd.to_datetime(self.df_by_instrument[figi]["time"], utc=True)

                history_df = await self.get_history_trades(client, instrument)
                self.df_by_instrument[figi] = merge_two_frames(self.df_by_instrument[figi], history_df)
            except Exception as ex:
                logger.error(ex)
        self.is_history_processed = False

    # загрузка последних доступных обезличенных сделок
    async def get_history_trades(self, client, instrument):
        history_df = create_empty_df()
        figi = instrument["figi"]
        current_date = now()
        time = 0

        while True:
            try:
                interval_from = current_date - timedelta(minutes=time + ONE_HOUR_TO_MINUTES)
                interval_to = current_date - timedelta(minutes=time)

                logger.info("instrument: %s, from: %s", instrument, interval_from)
                logger.info("instrument: %s, to: %s", instrument, interval_to)

                response = await client.market_data.get_last_trades(
                    figi=figi,
                    from_=interval_from,
                    to=interval_to,
                )
                logger.info("instrument: %s, size: %s", instrument, len(response.trades))
                if response is None or len(response.trades) == 0:
                    break

                for trade in response.trades:
                    processed_trade_df = processed_data(trade)
                    if processed_trade_df is not None:
                        history_df = pd.concat([history_df, processed_trade_df])
                history_df = history_df.sort_values("time")
                time += ONE_HOUR_TO_MINUTES
            except Exception as ex:
                logger.error(ex)
                break

        return history_df

    # основной метод для обработки входящих данных
    async def trades_stream(self, client):
        temp_df = {}
        for instrument in INSTRUMENTS:
            temp_df[instrument["figi"]] = create_empty_df()

        try:
            async for marketdata in client.market_data_stream.market_data_stream(
                    request_iterator(INSTRUMENTS)
            ):
                if not is_open_exchange():
                    logger.info("торговый день завершен, сохранение статистики")
                    self.order_service.write_statistics()
                    # todo добавить выход из приложения

                logger.info(marketdata)
                if marketdata is None:
                    continue
                trade = marketdata.trade
                if trade is None:
                    continue

                figi = trade.figi
                instrument = next(item for item in INSTRUMENTS if item["figi"] == figi)

                processed_trade_df = processed_data(trade)
                if processed_trade_df is not None:
                    # проверка позиций на закрытие по тейку/стопу
                    processed_trade = processed_trade_df.iloc[0]
                    price = processed_trade["price"]
                    time = processed_trade["time"]
                    self.order_service.processed_orders(instrument["name"], price, time)

                    if self.is_history_processed is True:
                        # пока происходит обработка истории - новые данные складываю во временную переменную
                        next_df = [temp_df[figi], processed_trade_df]
                        temp_df[figi] = pd.concat(next_df, ignore_index=True)
                    else:
                        # есть проблема, когда исторические данные загрузились, но в real-time они не приходят
                        # тогда исторические данные не окажутся в файле
                        if len(temp_df[figi]) > 0:
                            # если после обработки истории успели накопить real-time данные,
                            # то подмерживаю их и очищаю временную переменную
                            next_df = [self.df_by_instrument[figi], temp_df[figi], processed_trade_df]
                            self.df_by_instrument[figi] = pd.concat(next_df, ignore_index=True)
                            temp_df[figi].drop(temp_df[figi].index, inplace=True)

                            # отправляю обезличенные сделки на анализ
                            self.strategy[figi].set_df(self.df_by_instrument[figi])

                            file_path = get_file_path_by_instrument(instrument)
                            self.df_by_instrument[figi].to_csv(file_path, mode="w", header=True, index=False)
                        else:
                            # отправляю обезличенную сделку на анализ
                            # (алгоритм анализа можно заменить на любой)
                            # если ТВ подтвердится, то возвращается структура сделки
                            orders = self.strategy[figi].analyze(processed_trade_df)
                            if orders is not None:
                                for order in orders:
                                    self.order_service.create_order(order)

                            next_df = [self.df_by_instrument[figi], processed_trade_df]
                            self.df_by_instrument[figi] = pd.concat(next_df, ignore_index=True)

                        file_path = get_file_path_by_instrument(instrument)
                        processed_trade_df.to_csv(file_path, mode="a", header=False, index=False)
        except Exception as ex:
            logger.error(ex)

    async def main(self):
        UserService().show_settings()

        async with AsyncClient(TOKEN) as client:
            tasks = [asyncio.ensure_future(self.trades_stream(client)),
                     asyncio.ensure_future(self.sync_df(client))]
            await asyncio.wait(tasks)


if __name__ == "__main__":
    try:
        robot = TradingRobot()
        asyncio.run(robot.main())
    except Exception as ex:
        logger.error(ex)
