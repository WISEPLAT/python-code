"""This is an example on how to use the news fetcher module.
"""
from pytz import utc
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from tinvest_robot_perevalov import news_fetcher

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///../data/fetch-jobs.sqlite')
}

rss_feeds = [
    "https://www.investing.com/rss/news.rss",
    "https://www.investing.com/rss/stock.rss"
]

# We can use any scheduler here, but we use BlockingScheduler for simplicity.
scheduler = BlockingScheduler(jobstores=jobstores, timezone=utc)


def main():
    """Here we fetch and analyze the news each 5 minutes.
    """
    job = scheduler.add_job(news_fetcher.fetch_and_analyze, 'interval', [rss_feeds], minutes=5, next_run_time=datetime.datetime.now(tz=utc))
    scheduler.start()


if __name__ == "__main__":
    main()