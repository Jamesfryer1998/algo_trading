from ib_insync import *
import pandas as pd
from datetime import datetime
import time
import backtrader as bt


class LiveData:
    def __init__(self, ticker,  frequency):
        self.ticker = ticker
        self.ib = IB()
        self.connected = False
        self.data_frame = pd.DataFrame(columns=['timestamp', 'price'])
        self.frequency = frequency

    def fetch_forex_price(self, verbose=0):
        contract = Forex(self.ticker)
        self.ib.reqMktData(contract)
        ticker = self.ib.ticker(contract)
        self.ib.sleep(2)  # Adjust sleep time based on your latency and data availability

        price = ticker.marketPrice()
        if verbose == 1:
            print(f"{self.ticker} Price: {price}")

        if price is None:
            print(f"Failed to fetch price for {self.ticker}")
        return price

    def connect(self):
        if not self.connected:
            print("Connecting to IBKR...")
            self.ib.connect('127.0.0.1', 7497, clientId=1)
            print('IBKR Connected')
            self.connected = True

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

                # Using pd.concat instead of deprecated append
                new_df = pd.DataFrame([new_data])
                self.data_frame = pd.concat([self.data_frame, new_df], ignore_index=True)
                self.data_frame['price'] = self.data_frame['price'].astype(float)

                if len(self.data_frame) >= 15:
                    # Only start calculating RSI if we have more than one data point
                    rsi_signal = RSIOverboughtOversoldStrategy(self.data_frame)
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Signal: {rsi_signal}")
                elif len(self.data_frame) == 14:
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Starting on next run...")
                else:
                    print(f"Yielding data - Timestamp: {timestamp}, Price: {price}, Not enough data collected...")

                yield timestamp, price
                time.sleep(self.frequency)  # Adjust sleep duration for your requirements
            
            except Exception as e:
                print(f"Error fetching live data: {e}")
                time.sleep(5)  # Retry after a short delay in case of error

        self.disconnect()

def RSIOverboughtOversoldStrategy(data_frame, params=(14, 70, 30)):
    rsi_period, rsi_overbought, rsi_oversold = params

    # Calculate RSI
    delta = data_frame['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    data_frame['rsi'] = rsi

    # Last RSI value
    rsi_value = data_frame['rsi'].iloc[-1]

    if rsi_value >= rsi_overbought:
        return 2  # Sell signal
    elif rsi_value <= rsi_oversold:
        return 1  # Buy signal
    else:
        return 0  # Hold signal


def run_live_trading():
    print("Setting up live trading...")
    livedata = LiveData('GBPUSD', frequency=10)
    data_gen = livedata.get_live_data()
    for data in data_gen:
        # Here you can use the live data and trading signal to execute trades
        pass

if __name__ == "__main__":
    run_live_trading()