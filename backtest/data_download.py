import yfinance as yf
from datetime import datetime 
import backtrader as bt


class DownloadData():
    def __init__(self, ticker=None, fsym=None, tsym=None, from_date=None, to_date=None):
        self.ticker = ticker
        self.to_date = to_date
        self.from_date = from_date

    def get_data(self):
        data = bt.feeds.PandasData(dataname=yf.download(self.ticker, self.to_date, self.from_date, auto_adjust=True))
        return data
    
    def run(self):
        return self.get_data()