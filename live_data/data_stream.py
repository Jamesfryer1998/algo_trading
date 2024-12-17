import asyncio
import threading
import time as t
import pandas as pd
from ib_insync import *
from datetime import datetime, time
from strategies.live_strategies import *
from live_data.orderbook import OrderBook, Order
from validation.validate_order import ValidateOrder
from validation.validate_orderbook import ValidateOrderBook

# Global variable to control the running state
stop_event = threading.Event()

class LiveData:
    def __init__(self, ticker, api, frequency):
        self.ticker = ticker
        self.ib = api.ib  # Use the IB instance from IBKR_API
        self.api = api  # Store a reference to the IBKR_API instance
        self.data_frame = pd.DataFrame(columns=['timestamp', 'price'])
        self.frequency = frequency

    def fetch_forex_price(self, verbose=0):
        contract = Forex(self.ticker)
        self.ib.reqMktData(contract)
        ticker = self.ib.ticker(contract)
        self.ib.sleep(1)

        price = ticker.marketPrice()
        if verbose == 1:
            print(f"{self.ticker} Price: {price}")

        if price is None:
            print(f"Failed to fetch price for {self.ticker}")
        return price

    def get_live_data(self, selected_strategy_name):
        if not self.api.is_connected():
            self.api.connect()

        print(f"We have {selected_strategy_name} as the selected strategy")

        while True:
            try:
                price = self.fetch_forex_price()
                timestamp = datetime.now()
                new_data = {'timestamp': timestamp, 'price': price}
                strategy_class = STRATEGY_REGISTRY.get(selected_strategy_name)

                new_df = pd.DataFrame([new_data])
                if not self.data_frame.empty:
                    self.data_frame = pd.concat([self.data_frame, new_df], ignore_index=True)
                else:
                    self.data_frame = new_df

                self.data_frame['price'] = self.data_frame['price'].astype(float)

                # rsi_signal, rsi_value = None, None
                results = None, None

                if len(self.data_frame) >= 2:
                    results = strategy_class(self.data_frame)
                    if 'result' in self.data_frame.columns:
                        self.data_frame.loc[self.data_frame.index[-1], 'result'] = results[0]
                    else:
                        self.data_frame['result'] = results[0]

                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Indicator Value: {results[1]}, Signal: {results[0]}")
                elif len(self.data_frame) == 1:
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Starting on next run...")
                else:
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Not enough data collected...")

                yield timestamp, price, results[1], results[0]
                t.sleep(self.frequency)  # Adjust sleep duration for your requirements

            except Exception as e:
                print(f"Error fetching live data: {e}")
                t.sleep(self.frequency)  # Retry after a short delay in case of error

        self.disconnect()


def run_live_trading(ticker, amount, broker, selected_strategy_name, api, stop_event=None, update_ui_callback=None):
    print("************************************************")
    print(f"Setting up live trading on {broker}...")
    print(f"Selected strategy: {selected_strategy_name}")
    print(f"Ticker: {ticker}")
    print(f"Amount: {amount}")
    print("************************************************\n")

    if stop_event is None:
        stop_event = threading.Event()

    if update_ui_callback is None:
        # Define a default dummy callback if none is provided
        update_ui_callback = lambda price: print(f"Price updated: {price}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    livedata = LiveData(ticker, api, frequency=10)
    data_gen = livedata.get_live_data(selected_strategy_name)

    orderbook_filepath = 'live_data/data/OrderBook'
    orderbook = OrderBook(api, orderbook_filepath)

    while not stop_event.is_set():  # Check if stop_event is set
        current_time = datetime.now().time()
        start_time = time(6, 0)  # 6 AM
        end_time = time(22, 0)   # 10 PM

        if start_time <= current_time <= end_time:
            for timestamp, price, indicator_value, signal in data_gen:
                if stop_event.is_set():
                    break

                # Update the UI with the latest price
                update_ui_callback(price)

                # Create order
                order = Order(
                    date=timestamp,
                    ticker=ticker,
                    price=price,
                    amount=amount,
                    signal='TBD',
                    strategy='RSI',
                    status='Pending'
                )

                # Validate Order
                order_validator = ValidateOrder(
                    orderbook_filepath,
                    order,
                    expected_price=price,
                    expected_amount=amount,
                    num_orders_queued=1
                )

                result = order_validator.validate()

                if result is False:
                    pass

                if signal == 1:
                    api.buy(ticker, amount)
                    order.signal = 'BUY'
                    order.status = 'Filled'
                    # orderbook.add_order(order)
                    orderbook.get_order_and_add_to_orderbook(ticker)
                    
                elif signal == 2:
                    api.sell(ticker, amount)
                    order.signal = 'SELL'
                    order.status = 'Filled'
                    # orderbook.add_order(order)
                    orderbook.get_order_and_add_to_orderbook(ticker)

                else:
                    pass
        else:
            print("Trading hours are over.")
            break

    print("Live trading stopped.")
    api.disconnect()