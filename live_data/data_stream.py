import asyncio
import threading
import time as t
import pandas as pd
from ib_insync import *
from datetime import datetime, time
# from broker_API.IBKR_API import IBKR_API
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
        self.frequency = frequency - 1

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

    def get_live_data(self):
        if not self.api.is_connected():
            self.api.connect()

        while True:
            try:
                price = self.fetch_forex_price()
                timestamp = datetime.now()
                new_data = {'timestamp': timestamp, 'price': price}

                new_df = pd.DataFrame([new_data])
                if not self.data_frame.empty:
                    self.data_frame = pd.concat([self.data_frame, new_df], ignore_index=True)
                else:
                    self.data_frame = new_df

                self.data_frame['price'] = self.data_frame['price'].astype(float)

                rsi_signal, rsi_value = None, None

                if len(self.data_frame) >= 14:
                    rsi_signal, rsi_value = RSIOverboughtOversoldStrategy(self.data_frame)
                    self.data_frame['result'] = rsi_signal
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, RSI: {rsi_value}, Signal: {rsi_signal}")
                elif len(self.data_frame) == 13:
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Starting on next run...")
                else:
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Not enough data collected...")

                yield timestamp, price, rsi_value, rsi_signal
                t.sleep(self.frequency)  # Adjust sleep duration for your requirements

            except Exception as e:
                print(f"Error fetching live data: {e}")
                t.sleep(self.frequency)  # Retry after a short delay in case of error

        self.disconnect()


def run_live_trading(ticker, amount, broker, api, stop_event=None, update_ui_callback=None):
    print(f"Setting up live trading on {broker}...")

    if stop_event is None:
        stop_event = threading.Event()  # Create a stop event if none is provided

    if update_ui_callback is None:
        # Define a default dummy callback if none is provided
        update_ui_callback = lambda price: print(f"Price updated: {price}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    livedata = LiveData(ticker, api, frequency=10)
    data_gen = livedata.get_live_data()

    orderbook_filepath = 'live_data/data/OrderBook'
    orderbook = OrderBook(orderbook_filepath)

    while not stop_event.is_set():  # Check if stop_event is set
        current_time = datetime.now().time()
        start_time = time(6, 0)  # 6 AM
        end_time = time(22, 0)   # 10 PM

        if start_time <= current_time <= end_time:
            for timestamp, price, rsi, signal in data_gen:
                if stop_event.is_set():
                    break  # Exit the loop if stop_event is set

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
                validator = ValidateOrder(
                    orderbook_filepath,
                    order,
                    expected_price=price,
                    expected_amount=amount,
                    num_orders_queued=1
                )

                result = validator.validate()

                if result is False:
                    pass

                if signal == 1:
                    api.buy(ticker, amount)
                    order.signal = 'BUY'
                    order.status = 'Filled'
                    orderbook.add_order(order)
                    
                elif signal == 2:
                    api.sell(ticker, amount)
                    order.signal = 'SELL'
                    order.status = 'Filled'
                    orderbook.add_order(order)

                else:
                    pass
        else:
            print("Trading hours are over. Running orderbook validation...")
            validator = ValidateOrderBook(orderbook_filepath)            
            validator.validate()
            break

    print("Live trading stopped.")
    api.disconnect()



