from backtest.backtesting import *
from live_data.data_stream import *
from broker_API.IBKR_API import IBKR_API
from interface.user_interface import run_interface
from live_data.orderbook import OrderBook
from evaluation.evaluate_live_performance import EvaluateLivePerformance

def main():
    api = IBKR_API()
    run_interface(api)

    # backtest = Backtester()
    # backtest.fill_gaps()
    # backtest.run_backtest()
    # backtest.evaluate(30, "all")
    # run_live_trading("GBPUSD", 10000, "IBKR", api)
    # evaluator = Evaluation("backtest/data", 30)
    # evaluator.best_performing_strategy()

    # eval = EvaluateLivePerformance(api, 1)
    # print(eval.evaluate_new())


if __name__ == "__main__":
    main()