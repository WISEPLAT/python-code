from __future__ import annotations

import datetime
import logging
import pickle
import uuid

from abc import ABC, abstractmethod
from dataclasses import asdict

import pandas as pd

from tinkoff.invest import OrderState, Instrument, OrderDirection, Quotation, MoneyValue, OrderExecutionReportStatus, \
    OrderType

from robotlib.money import Money


class TradeStatisticsAnalyzer:
    PENDING_ORDER_STATUSES = [
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_PARTIALLYFILL
        ]

    trades: dict[str, OrderState]
    positions: int
    money: float
    instrument_info: Instrument
    logger: logging.Logger

    def __init__(self, positions: int, money: float, instrument_info: Instrument, logger: logging.Logger):
        self.trades = {}
        self.positions = positions
        self.money = money
        self.instrument_info = instrument_info
        self.logger = logger

    def add_trade(self, trade: OrderState) -> None:
        self.logger.debug(f'Updating balance. Current state: [positions={self.positions} money={self.money}]. '
                          f'trade: {trade}')

        if trade.order_id in self.trades:
            trade.direction = self.trades[trade.order_id].direction
            sign = 1 if trade.direction == OrderDirection.ORDER_DIRECTION_BUY else -1
            self.positions += (trade.lots_executed - self.trades[trade.order_id].lots_executed) * sign
            self.money -= (self.convert_from_quotation(trade.total_order_amount)
                           - self.convert_from_quotation(self.trades[trade.order_id].total_order_amount)) * sign
        else:
            sign = 1 if trade.direction == OrderDirection.ORDER_DIRECTION_BUY else -1
            self.positions += trade.lots_executed * sign
            self.money -= self.convert_from_quotation(trade.total_order_amount) * sign

        self.trades[trade.order_id] = trade
        self.logger.debug(f'Updating balance. New state: [positions={self.positions} money={self.money}]')

    def cancel_order(self, order_id: str):
        self.trades.pop(order_id)

    def get_positions(self) -> int:
        return self.positions

    def get_money(self) -> float:
        return self.money

    def get_pending_orders(self) -> list[OrderState]:
        return [trade for trade in self.trades.values() if trade.execution_report_status in self.PENDING_ORDER_STATUSES]

    def save_to_file(self, filename: str) -> None:
        with open(filename, 'wb') as file:
            pickle.dump(obj=self, file=file, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_from_file(filename: str) -> TradeStatisticsAnalyzer:
        with open(filename, 'rb') as file:
            return pickle.load(file)

    @staticmethod
    def convert_from_quotation(amount: Quotation | MoneyValue) -> float | None:
        if amount is None:
            return None
        return amount.units + amount.nano / (10 ** 9)

    def add_backtest_trade(self, quantity: int, price: Quotation, direction: OrderDirection):
        if quantity == 0:
            return
        price_money = MoneyValue('RUB', price.units, price.nano)
        zero_money = MoneyValue('RUB', 0, 0)
        self.add_trade(OrderState(
            order_id=str(uuid.uuid4()),
            execution_report_status=OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL,
            lots_requested=quantity,
            lots_executed=quantity,
            initial_order_price=price_money,
            executed_order_price=price_money,
            total_order_amount=(Money(price) * quantity).to_money_value('RUB'),
            average_position_price=price_money,
            initial_commission=zero_money,
            executed_commission=zero_money,
            figi=self.instrument_info.figi,
            direction=direction,
            initial_security_price=price_money,
            stages=[],
            service_commission=zero_money,
            currency=price_money.currency,
            order_type=OrderType.ORDER_TYPE_MARKET,
            order_date=datetime.datetime.now()
        ))

    def get_report(self, processors: list[TradeStatisticsProcessorBase] = None,
                   calculators: list[TradeStatisticsCalculatorBase] = None)\
            -> tuple[dict[str, any], pd.DataFrame]:
        df = pd.DataFrame(map(asdict, self.trades.values()))  # pylint:disable=invalid-name
        df['average_position_price'] = df['average_position_price'].apply(lambda x: x['units'] + x['nano'] / (10 ** 9))
        df['total_order_amount'] = df['total_order_amount'].apply(lambda x: x['units'] + x['nano'] / (10 ** 9))
        df['sign'] = 3 - df['direction'] * 2

        for processor in processors or []:
            df = processor.process(df)  # pylint:disable=invalid-name

        stats = {}
        for calculator in calculators or []:
            stats |= calculator.calculate(df)

        return stats, df


class TradeStatisticsProcessorBase(ABC):  # pylint:disable=too-few-public-methods
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:  # pylint:disable=invalid-name
        raise NotImplementedError()


class TradeStatisticsCalculatorBase(ABC):  # pylint:disable=too-few-public-methods
    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> dict[str, any]:  # pylint:disable=invalid-name
        raise NotImplementedError()


class BalanceProcessor(TradeStatisticsProcessorBase):  # pylint:disable=too-few-public-methods
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df['balance'] = -(df['total_order_amount'] * df['sign']).cumsum()
        df['instrument_balance'] = (df['lots_executed'] * df['sign']).cumsum()
        return df


class BalanceCalculator(TradeStatisticsCalculatorBase):  # pylint:disable=too-few-public-methods
    def calculate(self, df: pd.DataFrame) -> dict[str, any]:
        final_balance = df['balance'][len(df) - 1]
        final_instrument_balance = df['instrument_balance'][len(df) - 1]
        final_price = df['average_position_price'][len(df) - 1]
        return {
            'final_balance': final_balance,
            'max_loss': -df['balance'].min(),
            'final_instrument_balance': final_instrument_balance,
            'income': final_balance + final_instrument_balance * final_price
        }
