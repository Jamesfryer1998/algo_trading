import tkinter as tk
from tkinter import ttk
import sys
from live_data.data_stream import run_live_trading
from backtest.backtesting import Backtester
from broker_API.IBKR_API import IBKR_API
import threading


class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class TradingInterface:
    def __init__(self, root, api):
        self.root = root
        self.api = api
        self.initial_window_size = "1000x600"
        self.without_terminal_size = "380x600"
        self.stop_event = threading.Event()
        self.trading_thread = None
        self.initialise()

    def initialise(self):
        self.root.title("Trading Interface")
        self.root.geometry(self.initial_window_size)  # Initial window size

        # Create the left frame for the tabs and button
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Create the Notebook widget for tabs
        self.notebook = ttk.Notebook(self.left_frame)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a frame for each tab
        self.backtest_frame = ttk.Frame(self.notebook)
        self.evaluate_frame = ttk.Frame(self.notebook)
        self.live_trade_frame = ttk.Frame(self.notebook)

        # Add tabs to the Notebook
        self.notebook.add(self.backtest_frame, text="Backtest")
        self.notebook.add(self.evaluate_frame, text="Evaluation")
        self.notebook.add(self.live_trade_frame, text="Live Trading")

        # Initialize each tab with its content
        self.init_backtest_tab()
        self.init_evaluation_tab()
        self.init_live_trade_tab()

        # Add Toggle Terminal button under the Notebook in the left_frame
        self.toggle_terminal_button = tk.Button(self.left_frame, text="Toggle Terminal", command=self.toggle_terminal)
        self.toggle_terminal_button.pack(side=tk.TOP, pady=10)

        # Create terminal frame at the bottom (initially visible)
        self.terminal_frame = tk.Frame(self.root)
        self.terminal_text = tk.Text(self.terminal_frame, wrap=tk.WORD, height=10)
        self.terminal_text.pack(fill=tk.BOTH, expand=True)

        # Redirect stdout to the terminal text widget
        sys.stdout = RedirectText(self.terminal_text)

        # Pack the terminal frame so it's visible on startup
        self.terminal_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Start the periodic connection status check
        self.update_connection_status()

    def init_backtest_tab(self):
        run_button = tk.Button(self.backtest_frame, text="Run Backtest", command=self.run_backtest)
        run_button.pack(side=tk.BOTTOM, pady=20, padx=20)

    def init_evaluation_tab(self):
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

    def init_live_trade_tab(self):
        tk.Label(self.live_trade_frame, text="Enter Ticker:").pack(pady=10)
        self.ticker_entry = tk.Entry(self.live_trade_frame)
        self.ticker_entry.pack(pady=10)

        tk.Label(self.live_trade_frame, text="Enter Amount:").pack(pady=10)
        self.amount_entry = tk.Entry(self.live_trade_frame)
        self.amount_entry.pack(pady=10)

        tk.Label(self.live_trade_frame, text="Select Broker:").pack(pady=10)
        self.broker_var = tk.StringVar(value="IBKR")
        broker_dropdown = ttk.Combobox(self.live_trade_frame, textvariable=self.broker_var)
        broker_dropdown['values'] = ("IBKR",)
        broker_dropdown.pack(pady=10)

        run_button = tk.Button(self.live_trade_frame, text="Start Live Trading", command=self.live_trade)
        run_button.pack(side=tk.LEFT, pady=20, padx=20)

        stop_button = tk.Button(self.live_trade_frame, text="Stop Live Trading", command=self.stop_live_trade)
        stop_button.pack(side=tk.RIGHT, pady=20, padx=20)

        # Status label for connection status
        self.status_label = tk.Label(self.root, text="Disconnected", bg="red", fg="white", width=20)
        self.status_label.pack(pady=10)

    def run_backtest(self):
        backtest = Backtester()
        backtest.run_backtest()

    def evaluate_backtest(self):
        backtest = Backtester()
        eval_type = self.eval_type_var.get()

        if eval_type == "Ticker" and self.symbol_entry_frame:
            symbol = self.symbol_entry.get()
            backtest.evaluate(30, "ticker", ticker=symbol)
        else:
            backtest.evaluate(30, eval_type.lower())



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

        # Run the live trading in a separate thread
        self.trading_thread = threading.Thread(target=run_live_trading, args=(ticker, amount, broker, self.api, self.stop_event))
        self.trading_thread.start()

    def stop_live_trade(self):
        self.stop_event.set()  # Set the stop event to signal the thread to stop
        print("Stop signal sent for live trading.")

    def toggle_terminal(self):
        if self.terminal_frame.winfo_ismapped():
            self.terminal_frame.pack_forget()
            self.root.geometry(self.without_terminal_size)
        else:
            self.terminal_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.root.geometry(self.initial_window_size)

    def update_connection_status(self):
        # Update the connection status
        if self.api.is_connected():
            self.status_label.config(text="Connected", bg="green")
        else:
            self.status_label.config(text="Disconnected", bg="red")

        # Schedule the next update in 2 seconds
        self.root.after(5000, self.update_connection_status)


def run_interface(api):
    root = tk.Tk()
    app = TradingInterface(root, api)
    root.mainloop()
