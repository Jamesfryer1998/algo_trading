from live_data.data_stream import *
from backtest.backtesting import *
from backtest.evaluation import *


def main():
    # run_backtest()
    # run_live_trading("GBPUSD", 10000)

    # Evaluation
    data_dir = 'backtest/data'
    num_days = 30  # Number of days to go back
    evaluation = Evaluation(data_dir, num_days)
    evaluation.plot_average_pnl()
    # evaluation.plot_ticker_pnl('AAPL')


if __name__ == "__main__":
    main()
    