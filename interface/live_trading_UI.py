import threading
import tkinter as tk
from tkinter import ttk
from live_data.data_stream import run_live_trading
from backtest.evaluation import Evaluation
from strategies.live_strategies import live_strategy_list


class Live_trade_UI:
    def __init__(self, notebook, api, update_ticker_info):
        self.notebook = notebook
        self.api = api
        self.update_ticker_info = update_ticker_info
        self.backtest_data_path = "backtest/data"
        self.stop_event = threading.Event()

    def live_trade(self):
        self.stop_event.clear()  # Clear the stop event before starting

        ticker = self.ticker_entry.get()
        amount = self.amount_entry.get()
        broker = self.broker_var.get()

        if not ticker or not amount or not broker:
            print("Please fill in all the fields before starting live trading.")
            return

        try:
            amount = float(amount)
        except ValueError:
            print("Amount must be a number.")
            return

        # Run the live trading in a separate thread and pass the callback for updating the UI
        self.trading_thread = threading.Thread(target=run_live_trading, args=(
            ticker, amount, broker, self.api, self.stop_event, self.update_ticker_info))
        self.trading_thread.start()

    def stop_live_trade(self):
        self.stop_event.set()  # Set the stop event to signal the thread to stop
        print("Stop signal sent for live trading.")

    def _create_tab(self):
        self.live_trade_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.live_trade_frame, text="Live Trading")

    def _init_tab(self):
        tk.Label(self.live_trade_frame, text="Enter Ticker:").pack(pady=10)
        self.ticker_entry = tk.Entry(self.live_trade_frame)
        self.ticker_entry.pack(pady=10)
        self.ticker_entry.insert(0, "GBPUSD")  # Set default ticker value

        tk.Label(self.live_trade_frame, text="Enter Amount:").pack(pady=10)
        self.amount_entry = tk.Entry(self.live_trade_frame)
        self.amount_entry.pack(pady=10)
        self.amount_entry.insert(0, "10000")  # Set default amount value

        tk.Label(self.live_trade_frame, text="Select Broker:").pack(pady=10)
        self.broker_var = tk.StringVar(value="IBKR")
        broker_dropdown = ttk.Combobox(self.live_trade_frame, textvariable=self.broker_var)
        broker_dropdown['values'] = ("IBKR",)
        broker_dropdown.pack(pady=10)

        tk.Label(self.live_trade_frame, text="Strategy:").pack(pady=10)
        eval = Evaluation(self.backtest_data_path, 30)
        self.strategy_var = tk.StringVar(value=eval.best_performing_strategy())
        strategy_dropdown = ttk.Combobox(self.live_trade_frame, textvariable=self.strategy_var)
        strategy_dropdown['values'] = live_strategy_list()
        strategy_dropdown.pack(pady=10)

        run_button = tk.Button(self.live_trade_frame, text="Start Live Trading", command=self.live_trade)
        run_button.pack(side=tk.LEFT, pady=20, padx=20)

        stop_button = tk.Button(self.live_trade_frame, text="Stop Live Trading", command=self.stop_live_trade)
        stop_button.pack(side=tk.RIGHT, pady=20, padx=20)

    def _build_tab(self):
        self._create_tab()
        self._init_tab()