from pytz import utc
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from tinvest_robot_perevalov import trader

import os

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///../data/trade-jobs.sqlite')
}

account_id = os.environ["TINVEST_ACCOUNT_ID"]
tickers = os.environ["TINVEST_TICKERS"].split(",") # required to specify the tickers to trade

# We can use any scheduler here, but we use BlockingScheduler for simplicity.
scheduler = BlockingScheduler(jobstores=jobstores, timezone=utc)


def main():
    # trader.trade(tickers, account_id)
    job = scheduler.add_job(trader.trade, 'interval', [tickers, account_id], minutes=5, next_run_time=datetime.datetime.now(tz=utc))
    scheduler.start()


if __name__ == "__main__":
    main()