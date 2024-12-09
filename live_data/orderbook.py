import pandas as pd
from datetime import datetime
from validation.validate_orderbook import ValidateOrderBook

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
    def __init__(self, api, filepath):
        date = datetime.now().date()
        self.api = api
        self.ib = api.ib
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

    def match_orders(self, orderbook):
        """
        Match BUY and SELL orders in the orderbook to determine open and closed trades.
        Updates the 'Status' column for each row.
        """
        buy_orders = []
        sell_orders = []

        for idx, row in orderbook.iterrows():
            signal = row['Signal']
            amount = row['Amount']
            
            if signal == 'BUY':
                buy_orders.append(idx)  # Store index for later matching
            elif signal == 'SELL':
                sell_orders.append(idx)  # Store index for later matching

            # Match trades
            while buy_orders and sell_orders:
                buy_idx = buy_orders.pop(0)
                sell_idx = sell_orders.pop(0)

                buy_row = orderbook.loc[buy_idx]
                sell_row = orderbook.loc[sell_idx]

                matched_amount = min(buy_row['Amount'], sell_row['Amount'])

                # Update amounts
                orderbook.at[buy_idx, 'Amount'] -= matched_amount
                orderbook.at[sell_idx, 'Amount'] -= matched_amount

                # If fully matched, mark as closed
                if orderbook.at[buy_idx, 'Amount'] == 0:
                    orderbook.at[buy_idx, 'Status'] = 'Closed'
                if orderbook.at[sell_idx, 'Amount'] == 0:
                    orderbook.at[sell_idx, 'Status'] = 'Closed'

                # Reinsert partially matched orders
                if orderbook.at[buy_idx, 'Amount'] > 0:
                    buy_orders.insert(0, buy_idx)
                if orderbook.at[sell_idx, 'Amount'] > 0:
                    sell_orders.insert(0, sell_idx)

        # Mark remaining orders as open
        for idx in buy_orders + sell_orders:
            orderbook.at[idx, 'Status'] = 'Open'

    def get_order_and_add_to_orderbook(self, ticker):
        orderbook = self.load_orderbook()
        executions = self.ib.executions()

        if not executions:
            print("No executions retrieved from IBKR.")
            return

        # Convert IBKR executions to a DataFrame
        executions_df = pd.DataFrame([{
            'Date': pd.to_datetime(exec.time),
            'Ticker': ticker,
            'Price': exec.price,
            'Amount': exec.cumQty,
            'Signal': 'BUY' if exec.side == 'BOT' else 'SELL',  # Map signals
            'Strategy': 'N/A',  # Will add when we have a strat selector
            'Status': 'Filled'
        } for exec in executions])

        # Normalize date format and signals for comparison
        orderbook['Date'] = pd.to_datetime(orderbook['Date']).dt.tz_localize(None)
        executions_df['Date'] = executions_df['Date'].dt.tz_localize(None)

        # Identify new orders by comparing with the local orderbook
        comparison_columns = ['Date', 'Price', 'Amount', 'Signal']
        new_orders = executions_df.merge(
            orderbook[comparison_columns],
            on=comparison_columns,
            how='left',
            indicator=True
        ).query('_merge == "left_only"').drop(columns=['_merge'])

        if not new_orders.empty:
            # Append new orders to the local orderbook
            orderbook = pd.concat([orderbook, new_orders], ignore_index=True)
            # self.match_orders(orderbook) Only need to do this if using closed/open orders
            self.save_orderbook(orderbook)

            # Save the updated orderbook
            print(f"Added {len(new_orders)} new orders to the orderbook.")
        else:
            print("No new orders to add.")
        

    # For testing
    def connect(self):
        self.ib.connect('127.0.0.1', 7497, clientId=1)
        self.connected = True
        print('IBKR Connected')