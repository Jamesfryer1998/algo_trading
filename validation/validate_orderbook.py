import pandas as pd
from ib_insync import *
from datetime import datetime

class ValidateOrderBook:
    def __init__(self, filepath):
        self.filepath = filepath
        self.ib = IB()
        self.connected = False

    def load_orderbook(self):
        try:
            df = pd.read_csv(self.filepath)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Date', 'Ticker', 'Price', 'Amount', 'Signal', 'Strategy', 'Status'])
        return df

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

    def get_open_orders(self):
        self.connect()
        self.ib.reqAllOpenOrders()
        open_orders = self.ib.openOrders()
        self.disconnect()
        return open_orders

    def get_filled_orders(self):
        self.connect()
        # Define the time range for today's orders
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day).strftime('%Y%m%d')

        # Adding debug print to check the execution filter
        print(f"Requesting executions from: {today_start}")

        # Request executions with filter
        executions = self.ib.executions()

        print(f"Number of Orders found: {len(executions)}")

        self.disconnect()
        return executions

    def compare_orderbook(self):
        local_orderbook = self.load_orderbook()
        open_orders = self.get_open_orders()
        filled_orders = self.get_filled_orders()

        # Convert open orders to DataFrame
        open_orders_df = pd.DataFrame([{
            'Date': order.order.orderId,
            'Ticker': order.contract.symbol,
            'Price': order.order.lmtPrice,
            'Amount': order.order.totalQuantity,
            'Signal': order.order.action,
            'Strategy': order.order.orderType,
            'Status': 'Open'
        } for order in open_orders])

        # Convert filled orders to DataFrame
        filled_orders_df = pd.DataFrame([{
            'Date': exec.time,
            'Ticker': exec.contract.symbol,
            'Price': exec.price,
            'Amount': exec.shares,
            'Signal': exec.side,
            'Strategy': 'N/A',
            'Status': 'Filled'
        } for exec in filled_orders])

        combined_ibkr_orders = pd.concat([open_orders_df, filled_orders_df], ignore_index=True)

        # Compare with local orderbook
        comparison_result = local_orderbook.merge(combined_ibkr_orders, on=['Ticker', 'Price', 'Amount', 'Signal'], how='outer', indicator=True)

        # Print discrepancies
        print(comparison_result[comparison_result['_merge'] != 'both'])

    def validate(self):
        self.connect()
        self.compare_orderbook()
        self.disconnect()


# Example usage
if __name__ == "__main__":
    validator = ValidateOrderBook('live_data/data/OrderBook.csv')
    print(validator.get_filled_orders())
    # validator.validate()
