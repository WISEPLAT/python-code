import feedparser

from tinvest_robot_perevalov import _db
from tinvest_robot_perevalov.sentiment_analyzer import SentimentAnalyzer

import csv
import urllib.request
import os

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def _init_sentiment_analyzer() -> SentimentAnalyzer:
    """Internal method for initializing sentiment analyzer. To be extended in the future.

    Returns:
        SentimentAnalyzer: Initialized sentiment analyzer
    """
    MODEL = os.getenv('SENTIMENT_MODEL') or "cardiffnlp/twitter-roberta-base-sentiment"
    THRESHOLD = 0.1

    logger.info("Downloading labels...")
    
    labels=[]
    mapping_link = "https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode('utf-8').split("\n")
        csvreader = csv.reader(html, delimiter='\t')
    labels = [row[1] for row in csvreader if len(row) > 1]

    logger.info("Initializing sentiment analyzer...")
    
    return SentimentAnalyzer(MODEL, THRESHOLD, labels)

def fetch_and_analyze(rss_feeds: list):
    """
    Fetch news from RSS feeds, analyze sentiment, and save to database

    Args:
        rss_feeds (list): list of RSS feeds URLs to fetch
    """
    _db.init_db()
    sentiment_analyzer = _init_sentiment_analyzer()
    
    for feed in rss_feeds:
        entries = feedparser.parse(feed).entries
        for entry in entries:
            if not _db.check_if_exists(entry.title):
                sentiment = sentiment_analyzer.predict_sentiment(entry.title)
                _db.put_in_db(entry.title, sentiment)
                logger.info(f"TEXT: {entry.title} // SENTIMENT: {sentiment}")
