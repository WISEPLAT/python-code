# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 2022-07-22
### Removed
- Backtesting code has been moved to
[invest-tool](https://github.com/EIDiamond/invest-tools/tree/main/backtesting/tinkoff_historic_candles_py) project. 
- Removed working mode from configuration. 
Now, the bot project only for trading purposes. 
All other tools will be in tools repo [invest-tool](https://github.com/EIDiamond/invest-tools).   

## 2022-06-16
### Changed
- Trade logic and telegram api are working asynchronously. 
The main reason was telegram api is working pretty long, sometimes more than a few seconds.
After all changes telegram messages don't block trade logic.
- Changed dependencies: 
  - Removed 'python-telegram-bot'
  - Added 'aiogram' 
