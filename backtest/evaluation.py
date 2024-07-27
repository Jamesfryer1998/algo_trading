import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from utils.gmailer import send_email

class Evaluation:
    def __init__(self, data_dir, num_days):
        self.data_dir = data_dir
        self.num_days = num_days
        self.df = pd.DataFrame()  # Initialize an empty DataFrame

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
            self.df = pd.DataFrame()  # Reset df to an empty DataFrame if no data is found

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
            self.save_and_send_plot('average_pnl_plot.png', 'Average PnL Plot')
            self.delete_saved_plot('average_pnl_plot.png')

    def plot_ticker_pnl(self, ticker):
        if self.df.empty:
            self.load_data()

        if not self.df.empty:
            for strategy in self.df['strategy'].unique():
                strategy_data = self.df[self.df['strategy'] == strategy]
                data = strategy_data[strategy_data['ticker'] == ticker]
                plt.plot(data['date'], data['pnl'], marker='o', label=strategy)

            self.configure_plot(f'{ticker} PnL for Different Strategies (Last {self.num_days} Days)')
            self.save_and_send_plot(f'{ticker}_pnl_plot.png', f'{ticker} PnL Plot')
            self.delete_saved_plot(f'{ticker}_pnl_plot.png')

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

    def save_and_send_plot(self, image_path, plot_title):
        plt.savefig(image_path)  # Save the plot before showing it
        plt.show()  # Display the plot
        plt.close()
        recipient = "jamesfryer1998@gmail.com"
        subject = f'{plot_title} - Backtesting Results'
        content = f'Please find the attached plot of the {plot_title}.'
        send_email(recipient, subject, content, image_path)

    def delete_saved_plot(self, image_path):
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print("The file does not exist.")

# # Example usage
# if __name__ == "__main__":
#     data_dir = '/Users/james/Projects/algo_trading/backtest/data'
#     num_days = 30  # Number of days to go back
#     evaluation = Evaluation(data_dir, num_days)
#     evaluation.plot_average_pnl()
#     evaluation.plot_ticker_pnl('AAPL')
