import os
import pandas as pd
from datetime import datetime
from utils.json_tools import load_json, save_json

class EvaluateLivePerformance:
    def __init__(self, current_price, file_name=None, api=None):
        if api == None:
            self.ib = None
        else:
            self.api = api
            self.ib = api.ib
        self.current_price = current_price
        self.broker = "IBKR"
        self.commission = self.get_commission()
        self.data = None
        self.performance_file_path = f"evaluation/data/{datetime.now().date()}-perfMetrics.json"
        if file_name == None:
            self.file_name = f"live_data/data/OrderBook-{datetime.now().date()}.csv"
        else:
            self.file_name = file_name

    def load_data(self):
        """Load order book data using pandas."""
        if not os.path.exists(self.file_name):
            raise FileNotFoundError(f"Order book file {self.file_name} does not exist yet.")
        
        self.data = pd.read_csv(self.file_name)
        self.data["Price"] = self.data["Price"].astype(float)
        self.data["Amount"] = self.data["Amount"].astype(float)

    def get_commission(self):
        """Retrieve the commission multiplier from a JSON file."""
        data = load_json("broker_API/exchange_stats.json")
        return data[self.broker]["commission_currency"]

    def get_orderbook_stats(self):
        comission_payed = 0
        invested_amount = 0

        for _, trade in self.data.iterrows():
            price = trade["Price"]
            amount = trade["Amount"]
            invested_amount += amount
            commission = price * amount * self.commission
            comission_payed += commission

        return comission_payed, invested_amount
    
    async def evaluate_new_async(self):
            if self.ib.isConnected():
                self.load_data()
                return await self.get_stats_async()
            else:
                return 0.0, 0.0, 0.0

    async def get_stats_async(self):
        stats = await self.ib.accountSummaryAsync()
        currency = None
        realized = None
        unrealized = None
        for item in stats:
            if item.tag == "NetLiquidation":
                currency = item.currency

            if item.tag == "RealizedPnL" and item.currency == currency:
                realized = float(item.value)

            elif item.tag == "UnrealizedPnL" and item.currency == currency:
                unrealized = float(item.value)

        comission_payed, invested_amount = self.get_orderbook_stats()
        realized = realized - comission_payed
        roi = ((unrealized + realized) / invested_amount) * 100

        return realized, unrealized, roi

    def connect(self):
        self.ib.connect('127.0.0.1', 7497, clientId=1)
        self.connected = True
        print('IBKR Connected')

    def calculate_realized_profit(self):
        """
        Calculate realized profit based on filled orders.

        Returns:
            float: Total realized profit in USD.
        """
        realized_profit = 0.0

        for _, order in self.data.iterrows():  # Use iterrows for DataFrame iteration
            if order['Status'] == 'Closed':  # Use 'Closed' status to determine if the order is realized
                # Calculate profit for SELL orders
                if order['Signal'] == 'SELL':
                    profit = (order['Price'] - order.get('EntryPrice', order['Price'])) * order['Amount']
                # Calculate profit for BUY orders
                elif order['Signal'] == 'BUY':
                    profit = (order.get('EntryPrice', order['Price']) - order['Price']) * order['Amount']
                else:
                    continue

                profit -= self.commission * order['Amount']
                realized_profit += profit

        return realized_profit

    def calculate_unrealized_profit(self):
        """
        Calculate unrealized profit based on open positions and the current market price.

        Returns:
            float: Total unrealized profit in USD.
        """
        unrealized_profit = 0.0

        for _, order in self.data.iterrows():  # Use iterrows for DataFrame iteration
            if order['Status'] != 'Filled':  # Only include orders that are not yet realized
                continue

            if order['Signal'] == 'SELL':
                profit = (order['Price'] - self.current_price) * order['Amount']
            elif order['Signal'] == 'BUY':
                profit = (self.current_price - order['Price']) * order['Amount']
            else:
                continue

            profit -= self.commission * order['Amount']
            unrealized_profit += profit

        return unrealized_profit

    def calculate_roi(self, realized, unrealized):
        """
        Calculate return on investment (ROI).

        Returns:
            float: ROI percentage.
        """
        total_investment = sum(order['Price'] * order['Amount'] for _, order in self.data.iterrows() if order['Status'] in ['Filled', 'Closed'])
        if total_investment == 0:
            return 0.0

        total_profit = realized + unrealized
        roi = (total_profit / total_investment) * 100

        return roi
    
    def close_orders(self):
        """
        Match and close orders based on price-time priority.

        Modifies the 'Status' column of the DataFrame to 'Closed' for matched orders.
        """
        for i, order in self.data.iterrows():
            if order['Status'] != 'Filled':
                continue

            # Find the opposite signal to match
            opposite_signal = 'BUY' if order['Signal'] == 'SELL' else 'SELL'

            for j, match_order in self.data.iterrows():
                if (
                    match_order['Status'] == 'Filled' and
                    match_order['Signal'] == opposite_signal and
                    match_order['Date'] > order['Date']  # Prioritize earlier orders
                ):
                    # Match found, close both orders
                    self.data.at[i, 'Status'] = 'Closed'
                    self.data.at[j, 'Status'] = 'Closed'
                    break

    def save_performance(self, realized, unrealized, roi):
        new_data = {
            'DateTime': datetime.now().isoformat(),  # Convert to string for JSON
            'Strategy': str(self.data['Strategy'].iloc[0]),
            'Realized': realized,
            'Unrealized': unrealized,
            'ROI': roi
        }

        if os.path.exists(self.performance_file_path):
            past_data = load_json(self.performance_file_path)

            if not isinstance(past_data, list):
                past_data = [past_data]  # Convert dict to list if needed

            past_data.append(new_data)  # Append new entry
            new_data = past_data

        save_json(new_data, self.performance_file_path) 


    def evaluate(self):
        """Evaluate all performance metrics."""
        try:
            self.load_data()
        except FileNotFoundError as e:
            return 0.0, 0.0, 0.0

        self.close_orders()  # Ensure orders are matched and closed
        realized_profit = self.calculate_realized_profit()
        unrealized_profit = self.calculate_unrealized_profit()
        roi = self.calculate_roi(realized_profit, unrealized_profit)

        self.save_performance(realized_profit, unrealized_profit, roi)

        # print(f"Realized Profit: {realized_profit:.2f} USD")
        # print(f"Unrealized Profit: {unrealized_profit:.2f} USD")
        # print(f"ROI: {roi:.2f}%")

        return realized_profit, unrealized_profit, roi
