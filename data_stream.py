from ib_insync import *
import pandas as pd
from datetime import datetime, time
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers

from strategies.test_strategy import *


class LiveData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.ib = IB()
        self.ib.disconnect()
        self.date = None
        self.connected = False

    def fetch_forex_price(self, verbose=0):        
        contract = Forex(self.ticker)
        
        # Request market data
        self.ib.reqMktData(contract)

        # Wait for the price data to be received
        ticker = self.ib.ticker(contract)
        self.ib.sleep(10)

        # Retrieve the latest price
        price = ticker.marketPrice()

        if verbose == 1:
            print(f"{self.ticker} Price: {price}")

        # return price
            
        test_price = 1.45
        return test_price

    def concat_data(self, prev_df, next_df):
        new_df = pd.DataFrame(next_df)
        vertical_stack = pd.concat([prev_df, new_df], axis=0) 
        return vertical_stack
    
    def collect_data(self):
        date = datetime.now()
        price = self.fetch_forex_price()
        data = {'date': [date],
                'ticker': [self.ticker],
                'price': [price]}
        df = pd.DataFrame(data)
        return df
    
    def connect(self):
        if not self.connected:
            self.ib.connect('127.0.0.1', 7497, clientId=1)
            print('IBKR Connected')
            self.connected = True
        else:
            print('IBKR already connected')


    def disconnect(self):
        # Ensure we have dissconnected
        while self.ib.isConnected():
            self.ib.disconnect()
            print('IBKR Disconnected.')

    def run(self):
        self.connect()
        df = None
        while datetime.now().time() < time(23, 0):
            new_data = self.collect_data()
            df = self.concat_data(df, new_data)
            print(df)
            # return df

        print('Markets have closed.')

        self.disconnect()



class LiveTrading:
    def __init__(self, ticker, strategy):
        self.ticker = ticker
        self.strategy = strategy
        self.data = None
        self.live_data = LiveData(self.ticker)
        self.live_data.disconnect()
        self.cerebro = bt.Cerebro()

    def get_continuous_data(self):
        new_data = self.live_data.collect_data()
        self.data = self.live_data.concat_data(self.data, new_data)

    def check_time(self, time_to):
        if datetime.now().time() < time(time_to, 59):
            return True
        else:
            return False
    
    def add_data(self):
        data = btfeeds.PandasData(dataname=self.data)
        self.cerebro.adddata(data)
    
    def add_strategy(self):
        self.cerebro.addstrategy(self.strategy)

    def add_analyzer(self):
        self.cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='evaluation')

    def run(self):
        self.live_data.connect()

        # Configure Trader
        self.add_strategy()
        self.add_analyzer()

        # Continuously run and collect data
        while self.check_time(23):
            self.get_continuous_data()
            self.add_data()

            # Run Backtrader engine
            self.cerebro.run()

            # Extract signals from the strategy
            signals = self.cerebro.strategy.signal

            # Process signals
            if signals == 'buy':
                print("Buy signal detected")
                return True
            elif signals == 'sell':
                print("Sell signal detected")
                return False
            else:
                print("No signal or hold")
                return None

        print('Markets closed')

        self.live_data.disconnect()

LiveTrading('GBPUSD', SimpleMovingAverageStrategy).run()

    
# if __name__ == "__main__":
#     live_data = LiveData('GBPUSD')
#     live_data.run()