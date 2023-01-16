# Trading bot based on Tinkoff Invest Python gRPC client API

## Project Status
The project status is an example of trading bot and isn't ready for any production using. 


## Description
Here is trading bot for MOEX Exchange with ability to send information about trading to a telegram chat.
The bot is using [Tinkoff Invest Python gRPC client](https://github.com/Tinkoff/invest-python) api.

## Features
- Trading RUB stocks via [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) on MOEX Exchange 
- Ability to use personal trade strategy for every stock
- Trade information sends to a telegram chat (orders details, trade day summary etc.)

Note: trade strategy is represented in code is just example and not a trade or invest recommendation.     

## Before Start
### Dependencies

- [Tinkoff Invest Python gRPC client](https://github.com/Tinkoff/invest-python)
<!-- termynal -->
```
$ pip install tinkoff-investments
```
- [aiogram](https://docs.aiogram.dev/en/latest/)
<!-- termynal -->
```
$ pip install -U aiogram
```
### Brokerage account
Open brokerage account [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) and top up your account.

Do not forget to take TOKEN for API trading.

### Telegram (optional)
Register your bot via @BotFather.

Create a chat and get chat_id.

PS. Please use Google to find detailed instruction how to get chat_id.    

### Required configuration (minimal)
1. Open `settings.ini` file
2. Specify token for trade API in `TOKEN` (section `INVEST_API`)
3. (Optinal) Specify token for a telegram bot in `TELEGRAM_BOT_TOKEN` (section `BLOG`)
4. (Optinal) Specify id of a telegram chat in `TELEGRAM_CHAT_ID` (section `BLOG`)

### Run
Recommendation is to use python 3.10 (bot has been tested on 3.10 version include real trading). 

Run main.py

## Configuration
Configuration can be specified via settings.ini file.
### Section INVEST_API
Token and app name for [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) api.
### Section BLOG
- status - telegram working mode: 
  - 0 - disabled
  - 1 - enabled
- token and chat id for telegram api
### Section TRADING_ACCOUNT
Minimal amount of rub on account for start trading.
### Section TRADING_SETTINGS
Settings for time management. Bot trades only in main trade session. Bot ignore pre\post market etc. 
### Section Strategies
Settings for trade strategies.

Section STRATEGY_ticker_name:

- `STRATEGY_NAME` - name of algorithm
- `TICKER` - ticker name (human-friendly name for telegram messages)
- `FIGI` - figi of stock. Required for API
- `MAX_LOTS_PER_ORDER` - Maximum count of lots per order

Section STRATEGY_ticker_name_SETTINGS:

Detailed settings for strategy. Strategy class reads and parses settings manually.  

Note: Only one strategy for one stock in configuration.

## Trading on stocks exchange
Before start:
- Token verification
- Appropriate account selects automatically by token
- By trading schedule, bot selects time to start trading (start main trading session) 

Main session:
- Bot checks:
  - stock status for every stock (list of strategies from configuration)
  - minimum amount of rub on account
- Starts gRPC stream for data from API
- Strategies analyse candles and return signals if needed 
- Bot opens orders by signals from strategies
- If stop or take price levels are confirmed, bot closes orders

Trading schedule:
- Bot awaits start and end of main trading session
- Bot works every trade day 
- Restart doesn't require for trading. Only in emergency situations. 

## How to add a new strategy
- Write a new class with trade logic
- The new class must have IStrategy as super class 
- Give a name for the new class
- Extend StrategyFactory class by the name and return the new class by the name
- Specify new settings in settings.ini file. Put the new class name in `STRATEGY_NAME`
- Test the new class on historical candles

## Telegram messages
Information about:
- Trading day summary at start and list of stocks
- Open and close orders, take profit and stop loss price levels
- Trading day summary in the end of day

Telegram messages are optional and can be disabled without any effect on trading.

## Logging
All logs are written in logs/robot.log.
Any kind of settings can be changed in main.py code

## Project change log
[Here](CHANGELOG.md)

## Disclaimer
The author is not responsible for any errors or omissions, or for the trade results obtained from the use of this bot. 
