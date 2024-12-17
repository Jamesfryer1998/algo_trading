import os
import pandas as pd
import matplotlib.pyplot as plt
from utils.gmailer import send_email
from datetime import datetime, timedelta
from utils.html_filler import load_html_template

class EvaluateBacktest:
    def __init__(self, data_dir, num_days):
        self.data_dir = data_dir
        self.num_days = num_days
        self.df = pd.DataFrame()

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
            self.df = pd.concat(df_list, ignore_index=True)
            self.df.sort_values(by='date', inplace=True)
        else:
            print("No data found for the specified number of days.")
            self.df = pd.DataFrame()

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

    def save_plot(self, image_path):
        plt.savefig(image_path)

    def delete_saved_plot(self, image_path):
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print("The file does not exist.")

    def plot_average_pnl(self):
        if self.df.empty:
            self.load_data()
        if not self.df.empty:
            # Aggregate data by strategy and date, taking the average of pnl values
            aggregated_data = self.df.groupby(['date', 'strategy'])['pnl'].mean().reset_index()
            for strategy in aggregated_data['strategy'].unique():
                strategy_data = aggregated_data[aggregated_data['strategy'] == strategy]
                plt.plot(strategy_data['date'], strategy_data['pnl'], marker='o', label=strategy)
            self.configure_plot(f'Average PnL for Different Strategies (Last {self.num_days} Days)')
            self.save_plot('average_pnl_plot.png')
            plt.close()

    def plot_ticker_pnl(self, ticker):
        if self.df.empty:
            self.load_data()

        if not self.df.empty:
            for strategy in self.df['strategy'].unique():
                strategy_data = self.df[self.df['strategy'] == strategy]
                data = strategy_data[strategy_data['ticker'] == ticker]
                plt.plot(data['date'], data['pnl'], marker='o', label=strategy)

            self.configure_plot(f'{ticker} PnL for Different Strategies (Last {self.num_days} Days)')
            self.save_plot(f'{ticker}_pnl_plot.png')
            plt.close()

    def best_performing_ticker(self):
        if self.df.empty:
            self.load_data()
        if not self.df.empty:
            best_stocks = self.df.groupby('ticker')['pnl'].mean().nlargest(5).reset_index()
            print("Best Performing Stocks:")
            print(best_stocks)
            return best_stocks

    def worst_performing_ticker(self):
        if self.df.empty:
            self.load_data()
        if not self.df.empty:
            worst_stocks = self.df.groupby('ticker')['pnl'].mean().nsmallest(5).reset_index()
            print("Worst Performing Stocks:")
            print(worst_stocks)
            return worst_stocks
        
    def best_performing_strategy(self):
        self.load_data()
        
        avg_pnl_per_strategy = self.df.groupby('strategy')['pnl'].mean()
        sorted_strategies = avg_pnl_per_strategy.sort_values(ascending=False)
        top_strategy = sorted_strategies.idxmax()  # returns the strategy with the highest avg pnl
        
        return top_strategy
    
    def top_3_performing_strategies(self):
        self.load_data()
        
        avg_pnl_per_strategy = self.df.groupby('strategy')['pnl'].mean()
        sorted_strategies = avg_pnl_per_strategy.sort_values(ascending=False)   
        top_3_strategies = sorted_strategies.head(3)
        return top_3_strategies
        
    def send_summary_email(self):
        self.load_data()
        if self.df.empty:
            print("No data available for summary.")
            return

        # Generate and save plots
        self.plot_average_pnl()
        best_stocks = self.best_performing_ticker()
        worst_stocks = self.worst_performing_ticker()

        # Convert DataFrames to HTML
        best_stocks_html = best_stocks.to_html(index=False)
        worst_stocks_html = worst_stocks.to_html(index=False)

        # Load and fill the HTML template
        filled_html = load_html_template('utils/template.html', self.num_days, best_stocks_html, worst_stocks_html)

        # Send the email using yagmail
        send_email('Backtesting Results Summary', filled_html, ['average_pnl_plot.png'])

        # Delete the plot file after sending the email
        self.delete_saved_plot('average_pnl_plot.png')