from ib_insync import *


class IBKR_API:
    def __init__(self, connection=None):
        if connection is None:
            self.ib = IB()
            self.connected = False
        else:
            self.ib = connection
            self.connected = True

    def connect(self, host='127.0.0.1', port=7497, clientId=1):
        if not self.connected:
            try:
                print("Connecting to IBKR...")
                self.ib.connect(host, port, clientId=clientId)
                self.connected = True
                print('IBKR Connected')
            except Exception as e:
                print(f"Connection failed: {e}")
                self.connected = False

    def disconnect(self):
        if self.connected:
            try:
                print("Disconnecting from IBKR...")
                self.ib.disconnect()
                self.connected = False
                print('IBKR Disconnected')
            except Exception as e:
                print(f"Disconnection failed: {e}")

    def is_connected(self):
        return self.ib.isConnected()

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

        print(f'\n{"*" * 40}')
        print(f"Placing {action} order for {quantity} of {ticker}")
        trade = self.ib.placeOrder(contract, order)
        
        # Wait for order to be filled or canceled
        while trade.orderStatus.status not in ['Filled', 'Cancelled']:
            self.ib.sleep(1)
        
        print(f"Order {trade.orderStatus.status} with avgFillPrice: {trade.orderStatus.avgFillPrice}")
        print(f'{"*" * 40}\n')

        return trade

    def buy(self, ticker, quantity):
        return self.place_order(ticker, 'BUY', quantity)

    def sell(self, ticker, quantity):
        return self.place_order(ticker, 'SELL', quantity)
