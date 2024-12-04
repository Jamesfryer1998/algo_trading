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

    def get_open_orders(self):
        self.ib.reqAllOpenOrders()
        open_orders = self.ib.openOrders()
        return open_orders

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
        open_orders = self.get_open_orders()
        filled_orders = self.get_filled_orders()

        # Convert open orders to DataFrame
        if len(open_orders) > 0:
            open_orders_df = pd.DataFrame([{
                'Date': order.order.orderId,
                'Ticker': order.contract.symbol,
                'Price': order.order.lmtPrice,
                'Amount': order.order.totalQuantity,
                'Signal': order.order.action,
                'Strategy': order.order.orderType,
                'Status': 'Open'
            } for order in open_orders])
        else:
            open_orders_df = pd.DataFrame([])

        # Convert filled orders to DataFrame
        if len(filled_orders) > 0:
            filled_orders_df = pd.DataFrame([{
                'Date': exec.time,
                'Ticker': 'N/A',  # Filled orders don't have a ticker in your data
                'Price': exec.price,
                'Amount': exec.shares,
                'Signal': exec.side,
                'Strategy': 'N/A',
                'Status': 'Filled'
            } for exec in filled_orders])
        else:
            filled_orders_df = pd.DataFrame([])

        # Combine open and filled orders
        combined_ibkr_orders = pd.concat([open_orders_df, filled_orders_df], ignore_index=True)
        combined_ibkr_orders.replace(to_replace='BOT', value='BUY', inplace=True)
        combined_ibkr_orders.replace(to_replace='SLD', value='SELL', inplace=True)

        # Ensure both Date columns are of the same datetime type and round to seconds for matching
        local_orderbook['Date'] = pd.to_datetime(local_orderbook['Date']).dt.tz_localize(None).dt.floor('s')
        combined_ibkr_orders['Date'] = pd.to_datetime(combined_ibkr_orders['Date']).dt.tz_localize(None).dt.floor('s')

        # # Select only relevant columns for comparison
        # local_subset = local_orderbook[['Date', 'Amount', 'Signal']]
        # ibkr_subset = combined_ibkr_orders[['Date', 'Amount', 'Signal']]

        # # Identify differences (rows in IBKR orders not in local orderbook)
        # diff_ibkr_to_local = ibkr_subset.merge(local_subset, on=['Date', 'Amount', 'Signal'], how='outer', indicator=True)
        # new_rows = diff_ibkr_to_local[diff_ibkr_to_local['_merge'] == 'left_only'].drop(columns=['_merge'])

        # # Add the new rows back to the full orderbook with missing columns filled as needed
        # if not new_rows.empty:
        #     new_rows_full = new_rows.merge(combined_ibkr_orders, on=['Date', 'Amount', 'Signal'], how='left')
        #     # Append to local_orderbook
        #     updated_orderbook = pd.concat([local_orderbook, new_rows_full], ignore_index=True)

        #     # Save the updated orderbook back to the CSV
        #     # self.save_orderbook(updated_orderbook)

        #     print(f"Orderbook updated with {len(new_rows)} new rows.")
        # else:
        #     print("No new rows to add to the orderbook.")
