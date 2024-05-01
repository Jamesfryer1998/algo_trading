from datetime import datetime, timedelta
from backtest.initialise import Backtest
from strategies.test_strategy import *
import sys

sys.path.append('/Users/james/Projects/algo_trading/')

list_strats = [TestStrategy, 
               MAcrossover, 
               RSI2Strategy, 
               SimpleMovingAverageStrategy, 
               BreakoutStrategy, 
               BreakdownStrategy, 
               RSIOverboughtOversoldStrategy]

tickers = ["NVDA", "AAPL", "AMZN", "GOOGL"]
currencies = ["USD", "JPY", "LEV", "AUD", "CHF", "CAD", "GBP", "HKD", "NZD", "KRW"]
time = (datetime.today() - timedelta(days=5)).date()

def generate_combinations(strats, tickers, currencies, time):
    combinations = []

    for ticker in tickers:
        for strat in strats:
            combinations.append(Backtest(strat, ticker, to_date=time, interval='1m'))

    for currency_1 in currencies:
        for currency_2 in currencies:
            for strat in strats:
                if currency_1 != currency_2:
                        combinations.append(Backtest(strat, tsym=currency_1, fsym=currency_2, to_date=time, interval='1m'))

    return combinations

def run_backtests(combinations):
    for test in combinations:
        print(test.ticker)
        try:
            test.run()
        except ZeroDivisionError as e:
            print(f"Skipping {test.ticker}: {e}")
            continue

def print_pnl(combinations):
    for test in combinations:
        print(test.pnl)

combinations = generate_combinations(list_strats, tickers, currencies, time)
run_backtests(combinations)
print_pnl(combinations)