import sys
sys.path.append('/Users/james/Projects/algo_trading/')

from backtest.initialise import Backtest
from strategies.test_strategy import *
import backtrader.strategies as btstrats


# Backtest(MAcrossover, 'USD', 'GBP', to_date='2016-01-01').run()
# Backtest(btstrats.SMA_CrossOver, 'USD', 'GBP', to_date='2016-01-01').run()

Backtest(SimpleMovingAverageStrategy, 'NVDA',to_date='2019-07-01').run()

