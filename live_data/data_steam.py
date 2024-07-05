# import sys
# import os

# # Add the project root directory to the sys.path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# sys.path.append(project_root)

from strategies.test_strategy import *
# from ib_insync import *
# import backtrader as bt
from ib_insync import IB, Forex

# def fetch_forex_price(input_ticker, verbose=0):
#     ib = IB()
#     ib.disconnect()
#     ib.connect('127.0.0.1', 7497, clientId=1)  # Connect to IBKR TWS or IB Gateway
    
#     contract = Forex(input_ticker)
    
#     # Request market data
#     ib.reqMktData(contract)
#     # print(ib.accountSummary(account='DU8809497'))

#     # Wait for the price data to be received
#     ticker = ib.ticker(contract)
#     ib.sleep(10)

#     # Retrieve the latest price
#     price = ticker.marketPrice()

#     while ib.isConnected():
#         ib.disconnect()

#     if verbose == 1:
#         print(f"{input_ticker} Price: {price}")

#     return price

# if __name__ == '__main__':
#     while True:
#         price = fetch_forex_price('GBPUSD', 1)


class IBKRLiveData(bt.feeds.DataBase):
    lines = ('datetime', 'open', 'high', 'low', 'close', 'volume')
    params = (('input_ticker', 'GBPUSD'), ('client_id', 1), ('host', '127.0.0.1'), ('port', 7497))

    def __init__(self):
        super(IBKRLiveData, self).__init__()
        self.ib = IB()
        self.ib.disconnect()
        self.ib.connect(self.p.host, self.p.port, clientId=self.p.client_id)
        self.contract = Forex(self.p.input_ticker)
        self.ib.reqMktData(self.contract)

    def start(self):
        super(IBKRLiveData, self).start()

    def _load(self):
        ticker = self.ib.ticker(self.contract)
        if ticker is None:
            return False

        dt = bt.num2date(self.ib.serverTime())
        self.lines.datetime[0] = bt.date2num(dt)
        self.lines.open[0] = ticker.bid
        self.lines.high[0] = ticker.high
        self.lines.low[0] = ticker.low
        self.lines.close[0] = ticker.close
        self.lines.volume[0] = ticker.volume

        return True
    
class LiveTrading:
    def __init__(self, strategy, input_ticker='GBPUSD'):
        self.strategy = strategy
        self.input_ticker = input_ticker
        self.cerebro = bt.Cerebro()
        self.ib = IB()
        self.ib.disconnect()
        self.ib.connect('127.0.0.1', 7497, clientId=1)

    def add_data(self):
        data = IBKRLiveData(dataname=self.input_ticker)
        self.cerebro.adddata(data)

    def add_strategy(self):
        self.cerebro.addstrategy(self.strategy)

    def add_commission(self):
        self.cerebro.broker.setcommission(commission=0.00002) 

    def run(self):
        self.add_data()
        self.add_strategy()
        self.add_commission()

        self.cerebro.run()

        start_portfolio_value = self.cerebro.broker.getvalue()
        end_portfolio_value = self.cerebro.broker.getvalue()
        pnl = end_portfolio_value - start_portfolio_value

        print(f'Starting Portfolio Value: {start_portfolio_value:.2f}')
        print(f'Final Portfolio Value: {end_portfolio_value:.2f}')
        print(f'PnL: {pnl:.2f}')

if __name__ == '__main__':
    live_trading = LiveTrading(SimpleMovingAverageStrategy)
    live_trading.run()

