import datetime

import pytz as pytz
from dateutil import parser


def date_to_str(date):
    return date.isoformat()[:-3]+'Z'


def current_date():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc, microsecond=0)


def date_minus_days(date, days):
    return date - datetime.timedelta(days=days)


def date_minus_minutes(date, minutes):
    return date - datetime.timedelta(minutes=minutes)


def string_to_date(string_date):
    return parser.parse(string_date)

