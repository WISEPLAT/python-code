import asyncio
import datetime
import uuid

import tinkoff.invest

from src import settings
from src.containers.config import TraderConfig
from src.containers.market import (
    AccountBalance,
    CancelOrder,
    CreateOrder,
    MarketData,
    MarketState,
)
from src.service.errors import DecisionExecutionError
from src.traders.base import BaseTrader


class TraderRunner:
    @classmethod
    async def start_trader_loop(cls, trader: BaseTrader) -> None:
        """Start the trade loop with the given trader."""
        print("The trader has been started")
        while True:
            # fetch data from the market
            market_data = await cls._fetch_current_market_state(trader.trader_config)

            # make decisions in accordance with the strategy
            decisions = await trader.make_decisions(market_data)

            # execute decisions, if any
            await cls._execute_trader_decisions(decisions, trader.trader_config)

            # wait for the next step
            await asyncio.sleep(trader.trader_config.config["decision_interval_s"])

    @classmethod
    async def _fetch_current_market_state(cls, trader_config: TraderConfig) -> MarketState:
        async with tinkoff.invest.AsyncClient(
                settings.INVEST_TOKEN, sandbox_token=settings.SANDBOX_TOKEN, app_name=settings.APP_NAME
        ) as services:
            # orders book
            order_book = await services.market_data.get_order_book(
                figi=trader_config.instrument_figi, depth=trader_config.config["order_book_depth"]
            )

            # candles for required period
            now = datetime.datetime.utcnow()
            candles = (
                await services.market_data.get_candles(
                    figi=trader_config.instrument_figi,
                    from_=now - trader_config.candle_timedelta,
                    to=now,
                    interval=trader_config.candle_interval,
                )
            ).candles

            # available balance for the account
            positions = await services.operations.get_positions(account_id=trader_config.account_id)

            # orders
            orders = (await services.orders.get_orders(account_id=trader_config.account_id)).orders

            return MarketState(
                account_balance=AccountBalance(
                    money=positions.money,
                    securities=positions.securities,
                ),
                market_data=MarketData(
                    bids=order_book.bids,
                    asks=order_book.asks,
                    candles=candles,
                ),
                opened_orders=orders,
            )

    @classmethod
    async def _execute_trader_decisions(cls, decisions, trader_config):
        async with tinkoff.invest.AsyncClient(
                settings.INVEST_TOKEN, sandbox_token=settings.SANDBOX_TOKEN, app_name=settings.APP_NAME
        ) as services:
            for decision in decisions:
                # execute decision
                response = None
                try:
                    response = await cls._execute_decision(services, trader_config, decision)
                except DecisionExecutionError:
                    print("error executing decision")

                # log the decision and its execution result
                await cls._log_algorithm_decision(trader_config, decision, response)

    @classmethod
    async def _execute_decision(cls, client, trader_config, decision):
        if isinstance(decision, CreateOrder):
            try:
                return await client.orders.post_order(
                    order_id=str(uuid.uuid4()),
                    figi=trader_config.instrument_figi,
                    account_id=trader_config.account_id,
                    # decision
                    order_type=decision.order_type,
                    direction=decision.order_direction,
                    price=decision.price,
                    quantity=decision.quantity,
                )
            except Exception as exc:
                print("unable to post the order", str(exc))
        elif isinstance(decision, CancelOrder):
            try:
                return await client.orders.cancel_order(account_id=trader_config.account_id, order_id=decision.order_id)
            except Exception as exc:
                print("unable to cancel the order", str(exc))
        else:
            print("Unsupported decision type", type(decision))

    @classmethod
    async def _log_algorithm_decision(cls, trader_config, decision, response):
        with open(f"logs/{trader_config.account_id}.log", "a") as f:
            f.write(str(decision) + str(response))
