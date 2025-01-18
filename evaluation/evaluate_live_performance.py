import os
import pandas as pd
from datetime import datetime
from utils.json_tools import load_json

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

    # Maybe redundant
    # def calculate_realized_profit(self):
    #     """Calculate realized profit by matching closed trades."""
    #     realized_profit = 0
    #     buy_trades = []
    #     sell_trades = []

    #     for _, row in self.data.iterrows():
    #         signal = row["Signal"]
    #         price = row["Price"]
    #         amount = row["Amount"]
    #         commission = price * amount * self.commission

    #         if signal == "BUY":
    #             buy_trades.append((price, amount))
    #         elif signal == "SELL":
    #             sell_trades.append((price, amount))

    #         # Match trades (FIFO logic for simplicity)
    #         while buy_trades and sell_trades:
    #             buy_price, buy_amount = buy_trades.pop(0)
    #             sell_price, sell_amount = sell_trades.pop(0)

    #             matched_amount = min(buy_amount, sell_amount)
    #             realized_profit += (sell_price - buy_price) * matched_amount - commission

    #             # Adjust remaining amounts
    #             if buy_amount > sell_amount:
    #                 buy_trades.insert(0, (buy_price, buy_amount - matched_amount))
    #             elif sell_amount > buy_amount:
    #                 sell_trades.insert(0, (sell_price, sell_amount - matched_amount))

    #     return realized_profit

    # def calculate_unrealized_profit(self):
    #     """Calculate unrealized profit for open trades, accounting for commission."""
    #     unrealized_profit = 0
    #     capital = 0

    #     for _, trade in self.data.iterrows():
    #         if trade["Status"] == "Filled":
    #             price = trade["Price"]
    #             amount = trade["Amount"]
    #             commission = price * amount * self.commission

    #             if trade["Signal"] == "SELL":
    #                 # Unrealized profit for short position (SELL trade)
    #                 profit = (price - self.current_price) * amount
    #                 capital -= trade["Amount"]
    #             else:  # Long position for BUY signal
    #                 profit = (self.current_price - price) * amount
    #                 capital += trade["Amount"]

    #             # Deduct commission for open positions
    #             unrealized_profit += profit - commission

    #     if capital == 0:
    #         return 0

    #     return unrealized_profit
    

    # def calculate_roi(self):
    #     """Calculate ROI as a percentage."""
    #     realized_profit = self.calculate_realized_profit()
    #     unrealized_profit = self.calculate_unrealized_profit()

    #     buy_investment = (self.data.loc[self.data["Signal"] == "BUY", "Price"] * 
    #                     self.data.loc[self.data["Signal"] == "BUY", "Amount"]).sum()

    #     sell_proceeds = (self.data.loc[self.data["Signal"] == "SELL", "Price"] * 
    #                     self.data.loc[self.data["Signal"] == "SELL", "Amount"]).sum()

    #     net_investment = buy_investment - sell_proceeds

    #     # Avoid division by zero
    #     if net_investment == 0:
    #         return 0

    #     total_profit = realized_profit + unrealized_profit

    #     if net_investment < 0:
    #         # If the net investment is negative (i.e., from SELLs), use the negative sign correctly
    #         return (total_profit / abs(net_investment)) * 100
    #     else:
    #         return (total_profit / net_investment) * 100

    def calculate_realized_profit(self):
        """
        Calculate realized profit based on filled orders.

        Returns:
            float: Total realized profit in USD.
        """
        realized_profit = 0.0
        for order in self.data:
            if order['Status'] == 'Filled' and not order.get('is_closed', False):
                # Calculate profit for SELL orders
                if order['Signal'] == 'SELL':
                    profit = (order['Price'] - order.get('EntryPrice', order['Price'])) * order['Amount']
                # Calculate profit for BUY orders
                elif order['Signal'] == 'BUY':
                    profit = (order.get('EntryPrice', order['Price']) - order['Price']) * order['Amount']
                else:
                    continue

                realized_profit += profit

                # Mark order as closed
                order['is_closed'] = True

        self.realized_profit = realized_profit

    def calculate_unrealized_profit(self):
        """
        Calculate unrealized profit based on open positions and the current market price.

        Returns:
            float: Total unrealized profit in USD.
        """
        unrealized_profit = 0.0
        for order in self.data:
            if order['Status'] != 'Filled' or order.get('is_closed', False):
                continue

            if order['Signal'] == 'SELL':
                profit = (order['Price'] - self.current_price) * order['Amount']
            elif order['Signal'] == 'BUY':
                profit = (self.current_price - order['Price']) * order['Amount']
            else:
                continue

            unrealized_profit += profit

        self.unrealized_profit = unrealized_profit

    def calculate_roi(self):
        """
        Calculate return on investment (ROI).

        Returns:
            float: ROI percentage.
        """
        total_investment = sum(order['Price'] * order['Amount'] for order in self.data if order['Status'] == 'Filled')
        if total_investment == 0:
            return 0.0

        total_profit = self.realized_profit + self.unrealized_profit
        roi = (total_profit / total_investment) * 100

        return roi
    
    def close_orders(self):
        """
        Match and close orders based on price-time priority.

        Modifies the 'Status' column of the DataFrame to 'Closed' for matched orders.
        """
        for i, order in enumerate(self.data):
            if order['Status'] != 'Filled':
                continue

            # Find the opposite signal to match
            opposite_signal = 'BUY' if order['Signal'] == 'SELL' else 'SELL'

            for j, match_order in enumerate(self.data):
                if (
                    match_order['Status'] == 'Filled' and
                    match_order['Signal'] == opposite_signal and
                    match_order['Date'] > order['Date']  # Prioritize earlier orders
                ):
                    # Match found, close both orders
                    self.data[i]['Status'] = 'Closed'
                    self.data[j]['Status'] = 'Closed'
                    break

    def evaluate(self):
        """Evaluate all performance metrics."""
        try:
            self.load_data()
        except FileNotFoundError as e:
            return 0.0, 0.0, 0.0

        self.close_orders()  # Ensure orders are matched and closed
        self.calculate_realized_profit()
        self.calculate_unrealized_profit()
        roi = self.calculate_roi()

        print(f"Realized Profit: {self.realized_profit:.2f} USD")
        print(f"Unrealized Profit: {self.unrealized_profit:.2f} USD")
        print(f"ROI: {roi:.2f}%")

        return self.realized_profit, self.unrealized_profit, roi
