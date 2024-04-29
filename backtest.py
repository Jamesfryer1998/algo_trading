import sys
sys.path.append('/Users/james/Projects/algo_trading/')
from datetime import datetime, timedelta

from backtest.initialise import Backtest
from strategies.test_strategy import *
import backtrader.strategies as btstrats

list_strats = [TestStrategy, 
               MAcrossover, 
               RSI2Strategy,
               SimpleMovingAverageStrategy,
               BreakoutStrategy,
               BreakdownStrategy,
               RSIOverboughtOversoldStrategy]

tickers = ["NVDA", "AAPL"]

currencies = ["USD", "JPY", "LEV"]

time = (datetime.today() - timedelta(days=7)).date()

def generate_combinations(strats, tickers, currencies, time):
    combinations = []

    for ticker in tickers:
        for strat in strats:
            backtest = Backtest(strat, ticker, to_date=time, interval='1m')
            combinations.append(backtest)

    for currency_1 in currencies:
        for currency_2 in currencies:
            if currency_1 != currency_2:
                for strat in strats:
                    print(strat, currency_1, currency_2)
                    backtest = Backtest(strat, tsym=currency_1, fsym=currency_2, to_date=time, interval='1m')
                    combinations.append(backtest)

    return combinations

combinations = generate_combinations(list_strats, tickers, currencies, time)

for i in combinations:
    print(i.ticker)
    try:
        i.run()
    except ValueError as e:
        print(f"Skipping {i.ticker}: {e}")
        continue



# Testing
# Backtest(MAcrossover, 'USD', 'GBP', to_date='2016-01-01').run()
# Backtest(btstrats.SMA_CrossOver, 'USD', 'GBP', to_date='2016-01-01').run()
# Backtest(RSI2Strategy, 'NVDA', to_date='2024-03-05', interval='15m').run()
# Backtest(BreakoutStrategy, 'USD', 'GBP', to_date='2024-03-28', interval='1m').run()

# Backtest(BreakdownStrategy, 'USD', 'GBP', to_date='2023-03-28').run()
# Backtest(RSI2Strategy, 'USD', 'GBP', to_date='2024-03-28', interval='30m').run()
# Backtest(RSIOverboughtOversoldStrategy, 'USD', 'GBP', to_date='2024-04-21', interval='1m').run()
# Backtest(RSIOverboughtOversoldStrategy, 'NVDA', to_date=test, interval='1m').run()