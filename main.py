from live_data.data_stream import *
from backtest.backtesting import *


def main():
    backtest = Backtester()
    # backtest.run_backtest()
    backtest.evaluate(30, "all")
    # run_live_trading("GBPUSD", 10000)


if __name__ == "__main__":
    main()
    