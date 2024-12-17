import tkinter as tk
from tkinter import ttk
from evaluation.evaluate_live_performance import EvaluateLivePerformance

class Performance_tab:
    def __init__(self, notebook, root, api, get_current_price):
        self.notebook = notebook
        self.root = root
        self.api = api
        self.get_current_price = get_current_price

    def update_performance_indicators(self):
        if self.api.is_connected():
            current_price = self.get_current_price()
            if current_price is not None:
                eval = EvaluateLivePerformance(api=self.api, current_price=current_price)
                realized_profit_value, unrealized_profit_value, roi_value = eval.evaluate_new()

                self.roi_value_label.config(text=f"{roi_value:.3f}")
                self.unrealized_profit_value_label.config(text=f"{unrealized_profit_value:.3f}")
                self.realized_profit_value_label.config(text=f"{realized_profit_value:.3f}")

        # Always schedule the next check, regardless of connection status
        self.root.after(10000, self.update_performance_indicators)

    def _create_tab(self):
        self.performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_frame, text="Performance")

    def _init_tab(self):
        # Create Real-time ROI indicator
        self.roi_label = tk.Label(self.performance_frame, text="Real-time ROI:")
        self.roi_value_label = tk.Label(self.performance_frame, text="")
        self.roi_label.pack(pady=10)
        self.roi_value_label.pack(pady=10)

        # Create Unrealized Profit and Realized Profit indicators
        self.unrealized_profit_label = tk.Label(self.performance_frame, text="Unrealized Profit:")
        self.unrealized_profit_value_label = tk.Label(self.performance_frame, text="")
        self.realized_profit_label = tk.Label(self.performance_frame, text="Realized Profit:")
        self.realized_profit_value_label = tk.Label(self.performance_frame, text="")
        self.unrealized_profit_label.pack(pady=10)
        self.unrealized_profit_value_label.pack(pady=10)
        self.realized_profit_label.pack(pady=10)
        self.realized_profit_value_label.pack(pady=10)

        # Schedule updates for the performance indicators
        self.update_performance_indicators()

    def _build_tab(self):
        self._create_tab()
        self._init_tab()