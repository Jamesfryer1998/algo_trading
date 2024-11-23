import sys
import threading
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from strategies.live_strategies import *
from interface.backtest_tab import Backtest_tab
from interface.evaluation_tab import Evaluation_tab
from interface.live_trading_tab import Live_trade_tab
from interface.performance_tab import Performance_tab


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
        self.last_price = None
        self.initialise()

    def initialise(self):
        self.root.title("Trading Interface")
        self.root.geometry(self.initial_window_size) 
        self.small_font = tkFont.Font(size=11)

        self._create_left_frame()
        self._create_notebook()

        self.backtest_tab = Backtest_tab(self.notebook)
        self.evaluation_tab = Evaluation_tab(self.notebook)
        self.live_trade_tab = Live_trade_tab(self.notebook, self.api, self.update_ticker_info)
        self.performance_tab = Performance_tab(self.notebook, self.root, self.api, self.get_current_price)

        self.backtest_tab._build_tab()
        self.evaluation_tab._build_tab()
        self.live_trade_tab._build_tab()
        self.performance_tab._build_tab()

        self._create_toggle_terminal_button()
        self._create_ticker_frame()
        self._create_price_labels()
        self._create_terminal_frame()
        self._create_status_frame()

        self._update_connection_status()

    def _create_left_frame(self):
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.left_frame)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _create_toggle_terminal_button(self):
        self.toggle_terminal_button = tk.Button(self.left_frame, text="Toggle Terminal", command=self.toggle_terminal)
        self.toggle_terminal_button.pack(side=tk.TOP, pady=10)

    def _create_ticker_frame(self):
        self.ticker_frame = tk.Frame(self.root)
        self.ticker_frame.pack(side=tk.TOP, anchor="ne", padx=20, pady=10)  # Positioning at the top right

    def _create_price_labels(self):
        self.ticker_label = tk.Label(self.ticker_frame, text=f"Ticker: N/A", font=tkFont.Font(size=11))
        self.ticker_label.pack(side=tk.LEFT, padx=5)

        self.price_label = tk.Label(self.ticker_frame, text="Price: N/A", font=tkFont.Font(size=11))
        self.price_label.pack(side=tk.LEFT, padx=5)

        self.price_arrow = tk.Label(self.ticker_frame, text="-")  # Initially set to "-"
        self.price_arrow.pack(side=tk.LEFT, padx=5)

    def _create_terminal_frame(self):
        self.terminal_frame = tk.Frame(self.root)
        self.terminal_text = tk.Text(self.terminal_frame, wrap=tk.WORD, height=10)
        self.terminal_text.pack(fill=tk.BOTH, expand=True)

        # Redirect stdout to the terminal text widget
        sys.stdout = RedirectText(self.terminal_text)

        # Pack the terminal frame so it's visible on startup
        self.terminal_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_status_frame(self):
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Status label for connection status
        self.status_label = tk.Label(self.status_frame, text="Disconnected", bg="red", fg="white", width=20)
        self.status_label.pack(side=tk.TOP, pady=5)

        # Note label below the status label
        self.note_label = tk.Label(self.status_frame, text="Note: Connection established once trading is started", fg="light grey", font=tkFont.Font(size=11))
        self.note_label.pack(side=tk.TOP, pady=5)

    def _update_connection_status(self):
        # Update the connection status
        if self.api.is_connected():
            self.status_label.config(text="Connected", bg="green")
        else:
            self.status_label.config(text="Disconnected", bg="red")

        # Schedule the next update in 2 seconds
        self.root.after(5000, self._update_connection_status)

    def update_ticker_info(self, current_price):
        # This method is called by the background thread to update the UI.
        self.root.after(0, self._update_ui_elements, current_price)

    def _update_ui_elements(self, current_price):
        # Update the price and determine the arrow direction
        self.price_label.config(text=f"{current_price:.4f}")
        self.ticker_label.config(text=f"{self.live_trade_tab.ticker_entry.get()}")
        if self.last_price is not None:
            if current_price > self.last_price:
                self.price_arrow.config(text="↑", fg="green")
            elif current_price < self.last_price:
                self.price_arrow.config(text="↓", fg="red")
            else:
                self.price_arrow.config(text="-", fg="yellow")
        self.last_price = current_price

    def get_current_price(self):
        return self.last_price

    def toggle_terminal(self):
        if self.terminal_frame.winfo_ismapped():
            self.terminal_frame.pack_forget()
            self.root.geometry(self.without_terminal_size)
        else:
            self.terminal_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.root.geometry(self.initial_window_size)
            

def run_interface(api):
    root = tk.Tk()
    app = TradingInterface(root, api)
    root.mainloop()