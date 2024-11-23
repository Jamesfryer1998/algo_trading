from datetime import datetime
from utils.json_tools import load_csv
import os
import json

class EvaluatePerformance:
    def __init__(self):
        self.file_name = f"live_data/data/OrderBook-{datetime.now().date()}.csv"
        self.trades = []  # Stores all trades
        self.open_positions = {}  # Tracks open positions by ticker
        self.closed_trades = []  # Tracks closed trades for profit/loss calculation

    def load_data(self):
        if not os.path.exists(self.file_name):
            raise FileNotFoundError(f"Order book file {self.file_name} does not exist.")
        
        data = load_csv(self.file_name)
        print(data)

        for _, row in data.iterrows():
            trade = {
                'date': row["Date"],
                'ticker': row["Ticker"],
                'price': float(row["Price"]),
                'amount': float(row["Amount"]),
                'signal': row["Signal"],
                'strategy': row["Strategy"],
                'status': row["Status"]
            }
            self.trades.append(trade)
            self._process_trade(trade)

    def _process_trade(self, trade):
        ticker = trade['ticker']
        if trade['signal'] == 'BUY':
            # Add to open positions
            if ticker not in self.open_positions:
                self.open_positions[ticker] = []
            self.open_positions[ticker].append(trade)
        elif trade['signal'] == 'SELL':
            # Match against open BUY positions
            if ticker in self.open_positions and self.open_positions[ticker]:
                open_trade = self.open_positions[ticker].pop(0)  # FIFO matching
                closed_trade = {
                    'ticker': ticker,
                    'buy_price': open_trade['price'],
                    'sell_price': trade['price'],
                    'amount': trade['amount'],
                    'profit_loss': (trade['price'] - open_trade['price']) * trade['amount']
                }
                self.closed_trades.append(closed_trade)
            else:
                print(f"Unmatched SELL trade: {trade}")

    def calculate_profit_loss(self, last_prices=None):
        # Realized profit/loss
        total_realized_pnl = sum(trade['profit_loss'] for trade in self.closed_trades)
        
        # Unrealized profit/loss for open positions
        total_unrealized_pnl = 0
        if last_prices:
            for ticker, open_trades in self.open_positions.items():
                if ticker in last_prices:
                    for open_trade in open_trades:
                        unrealized_pnl = (last_prices[ticker] - open_trade['price']) * open_trade['amount']
                        total_unrealized_pnl += unrealized_pnl

        return total_realized_pnl, total_unrealized_pnl

    def calculate_average_gain_loss(self):
        if not self.closed_trades:
            return 0
        total_realized_pnl = sum(trade['profit_loss'] for trade in self.closed_trades)
        return total_realized_pnl / len(self.closed_trades)

    def save_performance_data(self, last_prices=None):
        total_realized_pnl, total_unrealized_pnl = self.calculate_profit_loss(last_prices)
        performance_data = {
            'total_realized_profit_loss': total_realized_pnl,
            'total_unrealized_profit_loss': total_unrealized_pnl,
            'average_realized_gain_loss': self.calculate_average_gain_loss(),
            'closed_trades': self.closed_trades,
            'open_positions': self.open_positions
        }
        with open('performance_data.json', 'w') as f:
            json.dump(performance_data, f, indent=4)

## Run from main like this
from evaluation.evaluate_performance import EvaluatePerformance

evaluator = EvaluatePerformance()
evaluator.load_data()
evaluator.save_performance_data() ## WHEN USING NEED TO GIVE THIS A LAST_PRICE, GET THIS FROM API
print(f"Total Profit/Loss: {evaluator.calculate_profit_loss()}")
print(f"Average Gain/Loss per Trade: {evaluator.calculate_average_gain_loss()}")