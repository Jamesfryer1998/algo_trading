import tkinter as tk
from tkinter import ttk
from backtest.backtesting import Backtester

class Evaluation_tab:
    def __init__(self, notebook):
        self.notebook = notebook

    def evaluate_backtest(self):
        backtest = Backtester()
        eval_type = self.eval_type_var.get()

        if eval_type == "Ticker" and self.symbol_entry_frame:
            symbol = self.symbol_entry.get()
            backtest.evaluate(30, "ticker", ticker=symbol)
        else:
            backtest.evaluate(30, eval_type.lower())
        
    def _create_tab(self):
        self.evaluate_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.evaluate_frame, text="Evaluation")

    def _init_tab(self):
        tk.Label(self.evaluate_frame, text="Select Evaluation Type:").pack(pady=10)

        self.eval_type_var = tk.StringVar(value="Average")
        eval_type_dropdown = ttk.Combobox(self.evaluate_frame, textvariable=self.eval_type_var)
        eval_type_dropdown['values'] = ("Average", "Ticker", "All")
        eval_type_dropdown.pack(pady=10)

        self.symbol_entry_frame = None

        def on_eval_type_change(event):
            if self.symbol_entry_frame:
                self.symbol_entry_frame.destroy()
                self.symbol_entry_frame = None

            if self.eval_type_var.get() == "Ticker":
                self.symbol_entry_frame = tk.Frame(self.evaluate_frame)
                self.symbol_entry_frame.pack(pady=10)
                tk.Label(self.symbol_entry_frame, text="Enter Ticker Symbol:").pack(pady=5)
                self.symbol_entry = tk.Entry(self.symbol_entry_frame)
                self.symbol_entry.pack(pady=5)

        eval_type_dropdown.bind("<<ComboboxSelected>>", on_eval_type_change)

        run_button = tk.Button(self.evaluate_frame, text="Run Evaluation", command=self.evaluate_backtest)
        run_button.pack(side=tk.BOTTOM, pady=20, padx=20)

    def _build_tab(self):
        self._create_tab()
        self._init_tab()