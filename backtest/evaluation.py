import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

class Evaluation:
    def __init__(self, data_dir, num_days):
        self.data_dir = data_dir
        self.num_days = num_days

    def load_data(self):
        end_date = datetime.today().date()

        df_list = []
        for i in range(self.num_days):
            date = (end_date - timedelta(days=i)).strftime("%d-%m-%Y")
            file_path = os.path.join(self.data_dir, f"{date}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df['date'] = pd.to_datetime(df['date'])
                df_list.append(df)
        
        if df_list:
            self.df = pd.concat(df_list)
        else:
            print("No data found for the specified number of days.")

    def plot_average_pnl(self):
        if not hasattr(self, 'df'):
            self.load_data()

        if hasattr(self, 'df') and not self.df.empty:
            # Aggregate data by strategy and date, taking the average of pnl values
            aggregated_data = self.df.groupby(['date', 'strategy'])['pnl'].mean().reset_index()

            for strategy in aggregated_data['strategy'].unique():
                strategy_data = aggregated_data[aggregated_data['strategy'] == strategy]
                plt.plot(strategy_data['date'], strategy_data['pnl'], marker='o', label=strategy)

        self.configure_plot(f'Average PnL for Different Strategies (Last {self.num_days} Days)')

    def plot_ticker_pnl(self, ticker):
        if not hasattr(self, 'df'):
            self.load_data()

        if hasattr(self, 'df') and not self.df.empty:
            for strategy in self.df['strategy'].unique():
                strategy_data = self.df[self.df['strategy'] == strategy]
                data = strategy_data[strategy_data['ticker'] == ticker]
                plt.plot(data['date'], data['pnl'], marker='o', label=strategy)

        self.configure_plot(f'{ticker} PnL for Different Strategies (Last {self.num_days} Days)')

    def configure_plot(self, title):
        plt.xlabel('Date')
        plt.ylabel('PnL')
        plt.title(title)
        plt.legend()
        plt.gca().set_facecolor('#f0f8ff')
        plt.grid(color='grey', linestyle='--', linewidth=0.5)
        min_date = (self.df['date'].min() - pd.Timedelta(days=1)).date()
        max_date = (self.df['date'].max() + pd.Timedelta(days=1)).date()
        plt.xlim(min_date, max_date)
        plt.xticks(rotation=45)
        plt.show()


# Example usage
data_dir = '/Users/james/Projects/algo_trading/backtest/data'
num_days = 30  # Number of days to go back
evaluation = Evaluation(data_dir, num_days)
evaluation.plot_average_pnl()
evaluation.plot_ticker_pnl('NVDA')