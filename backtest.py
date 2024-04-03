import sys
sys.path.append('/Users/james/Projects/algo_trading/')

from backtest.initialise import Backtest
from strategies.test_strategy import *
import backtrader.strategies as btstrats


# Backtest(MAcrossover, 'USD', 'GBP', to_date='2016-01-01').run()
# Backtest(btstrats.SMA_CrossOver, 'USD', 'GBP', to_date='2016-01-01').run()
# Backtest(RSI2Strategy, 'NVDA', to_date='2024-03-05', interval='15m').run()
# Backtest(BreakoutStrategy, 'USD', 'GBP', to_date='2024-03-28', interval='1m').run()

# Backtest(BreakdownStrategy, 'USD', 'GBP', to_date='2023-03-28').run()
# Backtest(RSI2Strategy, 'USD', 'GBP', to_date='2024-03-28', interval='30m').run()
Backtest(RSIOverboughtOversoldStrategy, 'USD', 'GBP', to_date='2024-03-28', interval='1m').run()
