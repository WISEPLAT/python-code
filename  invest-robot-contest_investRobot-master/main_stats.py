from robotlib.stats import BalanceProcessor, BalanceCalculator, TradeStatisticsAnalyzer


def main():
    stats = TradeStatisticsAnalyzer.load_from_file('/Users/egor/Dev/tinvest/robot/stats.pickle')

    short, full = stats.get_report(processors=[BalanceProcessor()], calculators=[BalanceCalculator()])

    print(full)
    print(short)


if __name__ == '__main__':
    main()
