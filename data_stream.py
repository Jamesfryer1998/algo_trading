from ib_insync import *
import pandas as pd
from datetime import datetime
import time
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
from strategies.test_strategy import *


class LiveData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.ib = IB()
        self.connected = False

    def fetch_forex_price(self, verbose=0):
        print(f"Fetching price for {self.ticker}...")
        contract = Forex(self.ticker)
        self.ib.reqMktData(contract)
        ticker = self.ib.ticker(contract)
        self.ib.sleep(2)  # Adjust sleep time based on your latency and data availability

        price = ticker.marketPrice()
        if verbose == 1:
            print(f"{self.ticker} Price: {price}")

        if price is None:
            print(f"Failed to fetch price for {self.ticker}")
        else:
            print(f"Fetched price for {self.ticker}: {price}")
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
                print(f"Yielding data - Timestamp: {timestamp}, Price: {price}")
                yield timestamp, price
                time.sleep(10)  # Adjust sleep duration for your requirements
            except Exception as e:
                print(f"Error fetching live data: {e}")
                time.sleep(10)  # Retry after a short delay in case of error
        self.disconnect()



class LiveDataFeed(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', -1),
    )

    def __init__(self, live_data_gen):
        self.live_data_gen = live_data_gen
        print("Initializing LiveDataFeed with live data generator...")
        super().__init__()

    def start(self):
        print("Starting LiveDataFeed...")
        self.iter = iter(self.live_data_gen)
        super().start()

    def _load(self):
        try:
            timestamp, price = next(self.iter)
            print(f"Loading data - Timestamp: {timestamp}, Price: {price}")
            self.lines.datetime[0] = bt.date2num(timestamp)
            self.lines.close[0] = price
            self.lines.open[0] = price
            self.lines.high[0] = price
            self.lines.low[0] = price
            self.lines.volume[0] = 0
            self.lines.openinterest[0] = 0
            return True
        except StopIteration:
            print("Live data generator exhausted.")
            return False
        except Exception as e:
            print(f"Error in _load: {e}")
            return False


def run_live_trading():
    print("Setting up live trading...")
    cerebro = bt.Cerebro()

    # Create and test the live data generator
    live_data_gen = LiveData('EURUSD').get_live_data()
    print("Live data generator created.")

    # Add live data feed
    live_data_feed = LiveDataFeed(dataname=pd.DataFrame(), live_data_gen=live_data_gen)
    cerebro.adddata(live_data_feed)
    print("Live data feed added to Cerebro.")

    # Add strategy
    cerebro.addstrategy(RSIOverboughtOversoldStrategy)
    print("Strategy added to Cerebro.")

    print("Starting Cerebro engine...")
    cerebro.run()
    print("Cerebro engine run completed.")

if __name__ == "__main__":
    run_live_trading()