import tkinter as tk
import sys
from live_data.data_stream import run_live_trading
from backtest.backtesting import Backtester

class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class TradingInterface:
    def __init__(self, root):
        self.root = root
        self.initialise()   

    def initialise(self ):
        self.root.title("Trading Interface")
        # Define window sizes
        self.window_with_terminal = "800x400"
        self.window_without_terminal = "400x400"

        self.root.geometry(self.window_with_terminal)  # Set the initial window size

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.terminal_frame = tk.Frame(self.root)
        self.terminal_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_width = 20
        button_height = 3

        backtest_button = tk.Button(self.button_frame, text="Backtest", command=self.run_backtest, width=button_width, height=button_height)
        backtest_button.pack(pady=10)

        evaluate_button = tk.Button(self.button_frame, text="Evaluate", command=self.evaluate_backtest, width=button_width, height=button_height)
        evaluate_button.pack(pady=10)

        live_trade_button = tk.Button(self.button_frame, text="Live Trade", command=self.live_trade, width=button_width, height=button_height)
        live_trade_button.pack(pady=10)

        self.toggle_terminal_button = tk.Button(self.button_frame, text="Toggle Terminal", command=self.toggle_terminal, width=10, height=2)
        self.toggle_terminal_button.pack(side=tk.BOTTOM, pady=10)

        self.terminal_text = tk.Text(self.terminal_frame, wrap=tk.WORD)
        self.terminal_text.pack(fill=tk.BOTH, expand=True)

        sys.stdout = RedirectText(self.terminal_text)

    def run_backtest(self):
        backtest = Backtester()
        backtest.run_backtest()

    def evaluate_backtest(self):
        backtest = Backtester()
        backtest.evaluate(30, "all")

    def live_trade(self):
        run_live_trading("GBPUSD", 10000)

    def toggle_terminal(self):
        if self.terminal_frame.winfo_viewable():
            self.terminal_frame.pack_forget()
            self.toggle_terminal_button.pack_forget()
            self.toggle_terminal_button.pack(side=tk.BOTTOM, pady=10)
            self.root.geometry(self.window_without_terminal)
        else:
            self.terminal_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.toggle_terminal_button.pack_forget()
            self.toggle_terminal_button.pack(in_=self.terminal_frame, side=tk.BOTTOM, pady=10)
            self.root.geometry(self.window_with_terminal)

def run_interface():
    root = tk.Tk()
    app = TradingInterface(root)
    root.mainloop()