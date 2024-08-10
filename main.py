from live_data.data_stream import *
from backtest.backtesting import *
from interface.user_interface import run_interface


def main():
    run_interface()
    # backtest = Backtester()
    # backtest.run_backtest()
    # backtest.evaluate(30, "all")
    # # run_live_trading("GBPUSD", 10000)


if __name__ == "__main__":
    main()
    