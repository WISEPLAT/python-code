import threading
from datetime import timedelta

import finplot as fplt
import numpy as np
import pandas as pd

from utils.strategy_util import ticks_to_cluster


class FinplotGraph(threading.Thread):
    def __init__(self, signal_cluster_period):
        super().__init__()

        self.signal_cluster_period = signal_cluster_period
        self.plots = {}
        self.ax = None

    def run(self):
        self.ax = fplt.create_plot("Tinkoff Invest profile touch strategy", maximize=False)
        self.ax.setLabel("right", "Цена")
        self.ax.setLabel("bottom", "Дата / время")
        fplt.show()

    def render(
            self,
            df: pd.DataFrame,
            valid_entry_points,
            invalid_entry_points,
            clusters=None
    ):
        candles = ticks_to_cluster(df, period=self.signal_cluster_period)

        # риски в свечах с максимальными объемами
        max_volumes = candles[["time", "max_volume_price"]]

        # не подтвержденные точки входа с разделением на лонг и шорт
        # округление времени точек входа для сопоставления с графиком
        round_invalid_times = [pd.to_datetime(time).ceil(self.signal_cluster_period) for time in invalid_entry_points]
        candles["invalid_buy_entry_point"] = np.where(
            candles["time"].isin(round_invalid_times) & (candles.shift()["direction"] == 1), candles["low"] - (
                    candles["low"] * 0.007 / 100), np.nan
        )
        candles["invalid_sell_entry_point"] = np.where(
            candles["time"].isin(round_invalid_times) & (candles.shift()["direction"] == 2), candles["high"] + (
                    candles["high"] * 0.007 / 100), np.nan
        )

        # подтвержденные точки входа с разделением на лонг и шорт
        # округление времени точек входа для сопоставления с графиком
        round_valid_times = [pd.to_datetime(time).ceil(self.signal_cluster_period) for time in valid_entry_points]
        candles["valid_buy_entry_point"] = np.where(
            candles["time"].isin(round_valid_times) & (candles.shift()["direction"] == 1), candles["low"] - (
                    candles["low"] * 0.007 / 100), np.nan
        )
        candles["valid_sell_entry_point"] = np.where(
            candles["time"].isin(round_valid_times) & (candles.shift()["direction"] == 2), candles["high"] + (
                    candles["high"] * 0.007 / 100), np.nan
        )

        if not self.plots:
            # первое построение графика
            self.plots["candles"] = (fplt.candlestick_ochl(candles))

            self.plots["max_volume_price"] = (
                fplt.plot(max_volumes["time"],
                          max_volumes["max_volume_price"],
                          style="d",
                          color="#808080",
                          ax=self.ax)
            )

            self.plots["invalid_buy_entry_point"] = (
                fplt.plot(candles["time"],
                          candles["invalid_buy_entry_point"],
                          style="^",
                          color="#000",
                          ax=self.ax,
                          legend="Не подходящая ТВ в лонг")
            )
            self.plots["invalid_sell_entry_point"] = (
                fplt.plot(candles["time"],
                          candles["invalid_sell_entry_point"],
                          style="v",
                          color="#000",
                          ax=self.ax,
                          legend="Не подходящая ТВ в шорт")
            )

            self.plots["valid_buy_entry_point"] = (
                fplt.plot(candles["time"],
                          candles["valid_buy_entry_point"],
                          style="^",
                          color="#4a5",
                          ax=self.ax,
                          legend="Подходящая ТВ в лонг")
            )
            self.plots["valid_sell_entry_point"] = (
                fplt.plot(candles["time"],
                          candles["valid_sell_entry_point"],
                          style="v",
                          color="#4a5",
                          ax=self.ax,
                          legend="Подходящая ТВ в шорт")
            )
        else:
            # обновление данных графика после первого построения
            # https://github.com/highfestiva/finplot/issues/131#issuecomment-786245998
            self.plots["candles"].update_data(candles, gfx=False)
            self.plots["max_volume_price"].update_data(max_volumes["max_volume_price"], gfx=False)
            self.plots["invalid_buy_entry_point"].update_data(candles["invalid_buy_entry_point"], gfx=False)
            self.plots["invalid_sell_entry_point"].update_data(candles["invalid_sell_entry_point"], gfx=False)
            self.plots["valid_buy_entry_point"].update_data(candles["valid_buy_entry_point"], gfx=False)
            self.plots["valid_sell_entry_point"].update_data(candles["valid_sell_entry_point"], gfx=False)

            for key, plot in self.plots.items():
                plot.update_gfx()

        if clusters is not None:
            for index, cluster in clusters.iterrows():
                cluster_time = cluster["time"]
                cluster_price = cluster["max_volume_price"]
                # todo прибавляю 55мин по той причине, что целый час еще не сформировался на графике
                #  крайней датой может быть 15:59:59.230333+00:00
                end_time = cluster_time + timedelta(minutes=55)
                fplt.add_line((cluster_time, cluster_price),
                              (end_time, cluster_price),
                              color="#80878787",
                              ax=self.ax)

        fplt.autoviewrestore()
