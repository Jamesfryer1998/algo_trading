import yfinance as yf
import backtrader as bt


class DownloadData():
    def __init__(self, ticker=None, fsym=None, tsym=None, from_date=None, to_date=None, interval=None):
        self.ticker = ticker
        self.to_date = to_date
        self.from_date = from_date
        self.interval = interval

    def get_data_feed(self):
        if self.interval is not None:
            try:
                data = yf.download(self.ticker, self.to_date, self.from_date, interval=self.interval, auto_adjust=True)
                self.data = bt.feeds.PandasData(dataname=data)
            except ValueError as e:
                print('No Data Found')
        else:
            try:
                data = yf.download(self.ticker, self.to_date, self.from_date, auto_adjust=True)
                self.data = bt.feeds.PandasData(dataname=data)
            except ValueError as e:
                print('No Data Found')

        return self.data
    
    def print_data(self):
        # Print data
        for i, d in enumerate(self.data):
            print("Data Point", i+1)
            print("Date:", d.datetime.date())
            print("Time:", d.datetime.time())
            print("High:", d.high)
            print("Low:", d.low)
            print("Open:", d.open)
            print("Close:", d.close)
            print("Volume:", d.volume)
            print("Open Interest:", d.openinterest)
            print("-" * 30)
    

    def run(self):
        return self.get_data_feed()