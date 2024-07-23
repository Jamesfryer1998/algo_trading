from ib_insync import *
import pandas as pd
from datetime import datetime
import time
from broker_API.IBKR_API import IBKR_API  # Ensure the path is correct
from live_data.orderbook import OrderBook


class LiveData:
    def __init__(self, ticker, frequency):
        self.ticker = ticker
        self.ib = IB()
        self.connected = False
        self.data_frame = pd.DataFrame(columns=['timestamp', 'price'])
        self.frequency = frequency

    def fetch_forex_price(self, verbose=0):
        contract = Forex(self.ticker)
        self.ib.reqMktData(contract)
        ticker = self.ib.ticker(contract)
        # self.ib.sleep(2)

        price = ticker.marketPrice()
        if verbose == 1:
            print(f"{self.ticker} Price: {price}")

        if price is None:
            print(f"Failed to fetch price for {self.ticker}")
        return price

    def connect(self):
        if not self.connected:
            print("Connecting to IBKR...")
            try:
                self.ib.connect('127.0.0.1', 7497, clientId=1)
                self.connected = True
                print('IBKR Connected')
            except Exception as e:
                print(f"API connection failed: {e}")
                self.connected = False
                raise

    def disconnect(self):
        if self.connected:
            print("Disconnecting from IBKR...")
            self.ib.disconnect()
            print('IBKR Disconnected')
            self.connected = False

    def get_live_data(self):
        self.connect()
        while True:
            try:
                price = self.fetch_forex_price(verbose=1)
                timestamp = datetime.now()
                new_data = {'timestamp': timestamp, 'price': price}

                new_df = pd.DataFrame([new_data])
                self.data_frame = pd.concat([self.data_frame, new_df], ignore_index=True)
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
                time.sleep(self.frequency)  # Adjust sleep duration for your requirements

            except Exception as e:
                print(f"Error fetching live data: {e}")
                time.sleep(5)  # Retry after a short delay in case of error

        self.disconnect()


# Move this out to own file
def RSIOverboughtOversoldStrategy(data_frame, params=(30, 75, 25)):
    rsi_period, rsi_overbought, rsi_oversold = params

    # Calculate RSI
    delta = data_frame['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Last RSI value
    rsi_value = rsi.iloc[-1]

    if rsi_value >= rsi_overbought:
        signal = 2  # Sell signal
    elif rsi_value <= rsi_oversold:
        signal = 1  # Buy signal
    else:
        signal = 0  # Hold signal

    return signal, rsi_value


def run_live_trading():
    print("Setting up live trading...")

    # Setting up live trading with ticker
    ticker = 'GBPUSD'
    amount = 10000
    livedata = LiveData(ticker, frequency=10)
    api = IBKR_API(livedata.ib)  # Pass the IB instance to IBKR_API
    data_gen = livedata.get_live_data()

    order_book = OrderBook('live_data/data/OrderBook')

    for timestamp, price, rsi, signal in data_gen:
        order = Order(
            date=timestamp,
            ticker=ticker,
            price=price,
            amount=amount,
            signal='TBD',
            strategy='RSI',  # Need to make live trading dynamic for the strategy passed in
            status='Pending'  # Set initial status to Pending, will update after checking with IBKR
        )

        if signal == 1:
            api.buy(ticker, amount)
            order.signal = 'BUY'
            order.status = 'Filled'  # Update status based on IBKR response
            order_book.add_order(order)
            
        elif signal == 2:
            api.sell(ticker, amount)
            order.signal = 'SELL'
            order.status = 'Filled'  # Update status based on IBKR response
            order_book.add_order(order)

        else:
            pass

if __name__ == "__main__":
    run_live_trading()


if __name__ == "__main__":
    run_live_trading()
