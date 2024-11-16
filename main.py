from backtest.backtesting import *
from live_data.data_stream import *
from broker_API.IBKR_API import IBKR_API
from interface.user_interface import run_interface

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


# if __name__ == "__main__":
#     main()

from evaluation.evaluate_performance import EvaluatePerformance

evaluator = EvaluatePerformance()
evaluator.load_data()
evaluator.save_performance_data() ## WHEN USING NEED TO GIVE THIS A LAST_PRICE, GET THIS FROM API
print(f"Total Profit/Loss: {evaluator.calculate_profit_loss()}")
print(f"Average Gain/Loss per Trade: {evaluator.calculate_average_gain_loss()}")