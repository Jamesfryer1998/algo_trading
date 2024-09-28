import tkinter as tk
from tkinter import ttk
from backtest.backtesting import Backtester

class Backtest_UI:
    def __init__(self, notebook):
        self.notebook = notebook

    def backfill_backtest(self):
        backtest = Backtester()
        backtest.fill_gaps()
        
    def run_backtest(self):
        backtest = Backtester()
        backtest.run_backtest()
        
    def _create_tab(self):
        self.backtest_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.backtest_frame, text="Backtest")


    def _init_tab(self):
        # Add label to display available backfill days
        backtest = Backtester()
        days_to_backfill = len(backtest.get_days_to_backfill())

        if days_to_backfill >= 2:
            backfill_info_text = f"Number of available days to backfill: {days_to_backfill}"
            backfill_label = tk.Label(self.backtest_frame, text=backfill_info_text, font=("Arial", 12))
            backfill_label.pack(side=tk.BOTTOM, pady=10)
            run_backtest_backfill_button = tk.Button(self.backtest_frame, text="Run Backfill Backtest", command=self.backfill_backtest)
            run_backtest_backfill_button.pack(side=tk.BOTTOM, pady=20, padx=20)

        run_backtest_button = tk.Button(self.backtest_frame, text="Run Backtest", command=self.run_backtest)
        run_backtest_button.pack(side=tk.BOTTOM, pady=20, padx=20)

    def _build_tab(self):
        self._create_tab()
        self._init_tab()