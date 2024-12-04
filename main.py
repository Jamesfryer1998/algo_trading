from backtest.backtesting import *
from live_data.data_stream import *
from broker_API.IBKR_API import IBKR_API
from interface.user_interface import run_interface
from live_data.orderbook import OrderBook

def main():
    api = IBKR_API()
    # run_interface(api)

    # backtest = Backtester()
    # backtest.fill_gaps()
    # backtest.run_backtest()
    # backtest.evaluate(30, "all")
    # run_live_trading("GBPUSD", 10000, "IBKR", api)
    # evaluator = Evaluation("backtest/data", 30)
    # evaluator.best_performing_strategy()

    order = Order(
        date="2024-12-04 22:41:29+00:00",
        ticker="TICKER",
        price=1,
        amount=1,
        signal='TBD',
        strategy='RSI',
        status='Pending'
    )

    orderbook = OrderBook(api, "live_data/data/OrderBook")
    orderbook.get_order_and_add_to_orderbook(order)


if __name__ == "__main__":
    main()