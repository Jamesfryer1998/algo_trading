from ib_insync import *
import time

class IBKR_API:
    def __init__(self, connection=None):
        if connection == None:
            self.ib = IB()
            self.connected = False
        else:
            self.ib = connection
            self.connected = True

    def connect(self, host='127.0.0.1', port=7497, clientId=1):
        if not self.connected:
            print("Connecting to IBKR...")
            self.ib.connect(host, port, clientId=clientId)
            print('IBKR Connected')

        self.connected = True

    def disconnect(self):
        if self.connected:
            print("Disconnecting from IBKR...")
            self.ib.disconnect()
            print('IBKR Disconnected')
            self.connected = False

    def place_order(self, ticker, action, quantity):
        """
        Place an order to buy or sell a specified quantity of a ticker.
        
        :param ticker: str, ticker symbol (e.g., 'GBPUSD')
        :param action: str, 'BUY' or 'SELL'
        :param quantity: float, number of units to buy or sell
        """
        if not self.connected:
            self.connect()

        contract = Forex(ticker)
        order = MarketOrder(action, quantity)

        print(f"Placing {action} order for {quantity} of {ticker}")
        trade = self.ib.placeOrder(contract, order)
        
        # Wait for order to be filled or canceled
        while trade.orderStatus.status not in ['Filled', 'Cancelled']:
            self.ib.sleep(1)
        
        print(f"Order {trade.orderStatus.status} with avgFillPrice: {trade.orderStatus.avgFillPrice}")

        return trade

    def buy(self, ticker, quantity):
        return self.place_order(ticker, 'BUY', quantity)

    def sell(self, ticker, quantity):
        return self.place_order(ticker, 'SELL', quantity)
