# Validating local orderbook with IBKR orderbook
# This is to check for failed orders, discrepencies in orders books. Also to save data for data vis and dashboard

import pandas as pd
from ib_insync import *
from datetime import datetime

class ValidateOrderBook:
    def __init__(self, api, filepath):
        self.filepath = filepath
        self.ib = api.ib
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

    def get_filled_orders(self):
        # Define the time range for today's orders
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day).strftime('%Y/%m/%d')
        executions = self.ib.executions()

        print(f"Requesting executions from: {today_start}")
        print(f"Number of Orders found: {len(executions)}")

        return executions


    def validate(self):
        local_orderbook = self.load_orderbook()
        filled_orders = self.get_filled_orders()

        if len(filled_orders) > 0:
            filled_orders_df = pd.DataFrame([{
                'Date': exec.time,
                'Ticker': 'N/A',
                'Price': exec.price,
                'Amount': exec.shares,
                'Signal': exec.side,
                'Strategy': 'N/A',
                'Status': 'Filled'
            } for exec in filled_orders])
        else:
            filled_orders_df = pd.DataFrame([])

        # Normalize formats for matching
        local_orderbook['Date'] = pd.to_datetime(local_orderbook['Date']).dt.tz_localize(None).dt.floor('s')
        filled_orders_df['Date'] = pd.to_datetime(filled_orders_df['Date']).dt.tz_localize(None).dt.floor('s')

        # Merge IBKR filled orders with the local orderbook
        combined_orders = pd.concat([local_orderbook, filled_orders_df], ignore_index=True)
        combined_orders.replace(to_replace={'BOT': 'BUY', 'SLD': 'SELL'}, inplace=True)

        # Save the updated order book
        combined_orders.to_csv(self.filepath, index=False)
        print(f"Order book validated and updated with statuses.")