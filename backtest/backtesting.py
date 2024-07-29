from datetime import datetime, timedelta
from backtest.initialise import Backtest
from strategies.test_strategy import *
import pandas as pd
from utils.gmailer import send_email
import os
import multiprocessing as mp
from backtest.evaluation import *


list_strats = [TestStrategy, 
               MAcrossover, 
               RSI2Strategy, 
               SimpleMovingAverageStrategy, 
               BreakoutStrategy, 
               BreakdownStrategy, 
               RSIOverboughtOversoldStrategy]

tickers = ["NVDA", "AAPL", "AMZN", "GOOGL"]
currencies = ["USD", "JPY", "LEV", "AUD", "CHF", "CAD", "GBP", "HKD", "NZD", "KRW"]

time = (datetime.today() - timedelta(days=5)).date()

def generate_combinations(strats, tickers, currencies, time):
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

def run_backtest_instance(object):
    try:
        object.run()
        result = capture_results(object)
        return result
    except ZeroDivisionError as e:
        print(f"Skipping {object.ticker}: {e}")
        return None

def capture_results(object):
    return {
        "ticker": object.ticker,
        "date": object.to_date,
        "strategy": strategy_to_string(object.strategy),
        "pnl": object.pnl
    }

def strategy_to_string(strategy):
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
        return "RSIOverboughtOversoldStrategy"
    if strategy == TestStrategy:
        return "RSIOverboughtOversoldStrategy"
    
def evaluate(num_days, type, ticker=None):
    data_dir = 'backtest/data'
    evaluation = Evaluation(data_dir, num_days)
    if type == "average":
        evaluation.plot_average_pnl()
    elif type == "ticker":
        evaluation.plot_ticker_pnl(ticker)
    elif type == "all":
        evaluation.send_summary_email()


def run_backtest(send_email=False):
    combinations = generate_combinations(list_strats, tickers, currencies, time)
    
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = pool.map(run_backtest_instance, combinations)
    
    results = [res for res in results if res is not None]
    df = pd.DataFrame(results)
    profitable_df = df[df["pnl"] > 1]

    file_path = 'backtest/data'
    today_date = datetime.now().strftime("%d-%m-%Y")
    file_name = os.path.join(file_path, f"{today_date}.csv")

    profitable_df.to_csv(file_name, index=False)
    if send_email:
        send_email("jamesfryer1998@gmail.com", "Backtesting complete", "Complete")
