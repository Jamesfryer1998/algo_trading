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

    def add_order(self, order):
        """
        Add a new order to the orderbook.
        :param order: Order, the order object containing order data
        """
        df = self.load_orderbook()
        new_order_df = order.order_to_df()
        df = pd.concat([df, new_order_df], ignore_index=True)
        self.save_orderbook(df)


# # Example usage
if __name__ == "__main__":

    order_book = OrderBook('live_data/data/OrderBook')
    
    new_order = Order(
        date=datetime.now(),
        ticker='GBPUSD',
        price=1.25,
        amount=100,
        signal='BUY',
        strategy='RSI',
        status='Filled'
    )
    
    order_book.add_order(new_order)
    print(order_book.load_orderbook())
