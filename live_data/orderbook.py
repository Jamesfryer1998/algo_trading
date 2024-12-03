import pandas as pd
from datetime import datetime


class Order:
    def __init__(self, date, ticker, price, amount, signal, strategy, status):
        self.date = date
        self.ticker = ticker
        self.price = price
        self.amount = amount
        self.signal = signal
        self.strategy = strategy
        self.status = status

    def order_to_df(self):
        df = pd.DataFrame({
            'Date': [self.date],
            'Ticker': [self.ticker],
            'Price': [self.price],
            'Amount': [self.amount],
            'Signal': [self.signal],
            'Strategy': [self.strategy],
            'Status': [self.status]
        })
        return df


class OrderBook:
    def __init__(self, filepath):
        date = datetime.now().date()
        self.filepath = f"{filepath}-{date}.csv"

    def save_orderbook(self, orderbook):
        """
        Save the orderbook to a CSV file.
        :param orderbook: pd.DataFrame, the orderbook data
        """
        orderbook.to_csv(self.filepath, index=False)

    def load_orderbook(self):
        """
        Load the orderbook from a CSV file.
        :return: pd.DataFrame, the loaded orderbook data
        """
        try:
            df = pd.read_csv(self.filepath)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Date', 'Ticker', 'Price', 'Amount', 'Signal', 'Strategy', 'Status'])
        return df

    def get_latest_price(self):
        """
        Get the latest price from the orderbook based on the timestamp.
        :return: float, the latest valid price or None if no valid price exists.
        """
        orderbook = self.load_orderbook()
        if not orderbook.empty:
            valid_prices = orderbook.dropna(subset=['Price'])
            if not valid_prices.empty:
                latest_row = valid_prices.iloc[-1]
                return latest_row['Price']
        return None

    def add_order(self, order):
        """
        Add a new order to the orderbook. Fill missing price with the latest valid price if necessary.
        :param order: Order, the order object containing order data
        """
        df = self.load_orderbook()

        if order.price is None or order.price == '':
            latest_price = self.get_latest_price()
            if latest_price is not None:
                order.price = latest_price
            else:
                print(f"No valid price found to fill for order: {order.__dict__}")
                return 

        new_order_df = order.order_to_df()
        df = pd.concat([df, new_order_df], ignore_index=True)
        self.save_orderbook(df)