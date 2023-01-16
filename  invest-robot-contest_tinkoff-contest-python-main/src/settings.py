import os

INVEST_TOKEN = os.getenv("INVEST_TOKEN")
SANDBOX_TOKEN = os.getenv("SANDBOX_TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
APP_NAME = os.getenv("APP_NAME")

FIGI = os.getenv("FIGI")

assert INVEST_TOKEN is not None
assert SANDBOX_TOKEN is not None
