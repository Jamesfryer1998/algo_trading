import os
import json
import numpy as np
import pandas as pd
import multiprocessing as mp
from utils.gmailer import send_email
from strategies.test_strategy import *
from datetime import datetime, timedelta
from backtest.initialise import Backtest
from backtest.evaluation import Evaluation

class Backtester:
    list_strats = [
        TestStrategy, 
        MAcrossover, 
        RSI2Strategy, 
        SimpleMovingAverageStrategy, 
        BreakoutStrategy, 
        BreakdownStrategy, 
        RSIOverboughtOversoldStrategy
    ]

    def __init__(self):
        self.data_file_path = "backtest/data"
        self.symbols_file_path = "backtest/symbols.json"
        self.time = (datetime.today() - timedelta(days=5)).date()
        self.tickers, self.currencies = self.load_symbols()

    def load_symbols(self):
        with open(self.symbols_file_path, 'r') as file:
            symbols = json.load(file)
        return symbols['tickers'], symbols['forex']

    def generate_combinations(self, strats, tickers, currencies, time):
        combinations = []

        for ticker in tickers:
            for strat in strats:
                combinations.append(Backtest(strat, ticker, to_date=time, interval='1m'))

        for currency_1 in currencies:
            for currency_2 in currencies:
                for strat in strats:
                    if currency_1 != currency_2:
                        combinations.append(Backtest(strat, tsym=currency_1, fsym=currency_2, to_date=time, interval='1m'))

        return combinations

    def run_backtest_instance(self, object):
        try:
            object.run()
            result = self.capture_results(object)
            return result
        except ZeroDivisionError as e:
            print(f"Skipping {object.ticker}: {e}")
            return None

    def capture_results(self, object):
        return {
            "ticker": object.ticker,
            "date": object.to_date,
            "strategy": self.strategy_to_string(object.strategy),
            "pnl": object.pnl
        }

    def strategy_to_string(self, strategy):
        if strategy == TestStrategy:
            return "TestStrategy"
        if strategy == SimpleMovingAverageStrategy:
            return "SimpleMovingAverageStrategy"
        if strategy == MAcrossover:
            return "MAcrossover"
        if strategy == RSI2Strategy:
            return "RSI2Strategy"
        if strategy == BreakoutStrategy:
            return "BreakoutStrategy"
        if strategy == BreakdownStrategy:
            return "BreakdownStrategy"
        if strategy == RSIOverboughtOversoldStrategy:
            return "RSIOverboughtOversoldStrategy"
    
    def evaluate(self, num_days, type, ticker=None):
        evaluation = Evaluation(self.data_file_path, num_days)
        if type == "average":
            evaluation.plot_average_pnl()
        elif type == "ticker":
            evaluation.plot_ticker_pnl(ticker)
        elif type == "all":
            evaluation.send_summary_email()

    def get_days_to_backfill(self):
        current_date = datetime.now().date()

        data_files = os.listdir(self.data_file_path)
        date_strs = [file.replace('.csv', '') for file in data_files]
        latest_data_date = max([datetime.strptime(date_str, '%d-%m-%Y').date() for date_str in date_strs])

        latest_data_date_str = latest_data_date.strftime('%d-%m-%Y')
        current_date_str = current_date.strftime('%d-%m-%Y')

        # Max days to look back in yfinance at 1min intervals is 7 days
        max_days_backfill = 6
        backfill_start_date = max(latest_data_date, current_date - timedelta(days=max_days_backfill))
        dates = pd.date_range(start=backfill_start_date, end=current_date)
        days_to_backfill = [date.date() for date in dates if date.isoweekday() in [1, 2, 3, 4, 5]]

        return days_to_backfill

    def fill_gaps(self):
        """
        This method fills gaps in backtesting data, from the latest data date to the current date.
        It interpolates the missing values in the data to maintain continuity, but only for the past 7 days.
        """
        days_to_backfill = self.get_days_to_backfill()
        print(f"Backfilling data for dates: {days_to_backfill}")

        if len(days_to_backfill) != 0:
            for date in days_to_backfill:
                print(f"Providing backtest backfill for {date.strftime('%d-%m-%Y')}")
                file_name = os.path.join(self.data_file_path, f"{date.strftime('%d-%m-%Y')}.csv")
                combinations = self.generate_combinations(self.list_strats, self.tickers, self.currencies, date)
                
                with mp.Pool(processes=mp.cpu_count()) as pool:
                    results = pool.map(self.run_backtest_instance, combinations)

                results = [res for res in results if res is not None]
                df = pd.DataFrame(results)
                profitable_df = df[df["pnl"] > 1]
                profitable_df.to_csv(file_name, index=False)
        
        send_email("jamesfryer1998@gmail.com", "Backtesting backfill complete", f"{len(days_to_backfill)} days backfilled with backtesting.")
        

    def run_backtest(self, send_email=False):
        combinations = self.generate_combinations(self.list_strats, self.tickers, self.currencies, self.time)
        
        with mp.Pool(processes=mp.cpu_count()) as pool:
            results = pool.map(self.run_backtest_instance, combinations)
        
        results = [res for res in results if res is not None]
        df = pd.DataFrame(results)
        profitable_df = df[df["pnl"] > 1]

        today_date = datetime.now().strftime("%d-%m-%Y")
        file_name = os.path.join(self.data_file_path, f"{today_date}.csv")

        profitable_df.to_csv(file_name, index=False)
        if send_email:
            send_email("jamesfryer1998@gmail.com", "Backtesting complete", "Complete")