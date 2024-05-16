from datetime import datetime, timedelta
from backtest.initialise import Backtest
from strategies.test_strategy import *
import pandas as pd
from utils.gmailer import send_email
import os

list_strats = [TestStrategy, 
               MAcrossover, 
               RSI2Strategy, 
               SimpleMovingAverageStrategy, 
               BreakoutStrategy, 
               BreakdownStrategy, 
               RSIOverboughtOversoldStrategy]

tickers = ["NVDA", "AAPL", "AMZN", "GOOGL"]
currencies = ["USD", "JPY", "LEV", "AUD", "CHF", "CAD", "GBP", "HKD", "NZD", "KRW"]

# tickers = ["NVDA"]
# currencies = ["USD", "JPY"]

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

def run_backtests(combinations):
    results = []
    for object in combinations:
        print(object.ticker)
        try:
            object.run()
            capture_results(object, results)
        except ZeroDivisionError as e:
            print(f"Skipping {object.ticker}: {e}")
            continue

    return results

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

def capture_results(object, results):
    result = {"ticker": object.ticker,
          "date": object.to_date,
          "strategy": strategy_to_string(object.strategy),
          "pnl": object.pnl}
    results.append(result)

def run_backtest():
    combinations = generate_combinations(list_strats, tickers, currencies, time)
    df = pd.DataFrame(run_backtests(combinations))
    profitablf_df = df[df["pnl"] > 1]

    file_path = 'backtest/data'
    today_date = datetime.now().strftime("%d-%m-%Y")
    file_name = os.path.join(file_path, f"{today_date}.csv")

    profitablf_df.to_csv(file_name, index=False)

run_backtest()

send_email("jamesfryer1998@gmail.com", "Backtesting complete", "Complete")
# print(df)