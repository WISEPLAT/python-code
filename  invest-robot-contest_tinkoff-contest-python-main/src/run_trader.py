import argparse
import asyncio

import yaml

from src.service.config import prepare_trader_config
from src.service.trader import TraderRunner
from src.traders.base import load_trader_class


async def main():
    # parse input args
    parser = argparse.ArgumentParser()
    parser.add_argument("trader")
    parser.add_argument("-c", "--config")
    args = parser.parse_args()

    # find the trader by file name
    trader_cls = load_trader_class(args.trader)

    # load the trader's config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    # initialize the trader
    trader_config = await prepare_trader_config(config)
    trader = trader_cls(trader_config)

    # start the trader
    if input(trader.initial_message()) == "yes":
        await TraderRunner.start_trader_loop(trader)
    else:
        print("Declined. Trader hasn't been started")


if __name__ == "__main__":
    asyncio.run(main())
