import numpy as np
from backtest.data_download import *
from strategies.test_strategy import *
import backtrader.analyzers as btanalyzers


class Backtest():
    def __init__(self, strategy, ticker=None, tsym=None, fsym=None, to_date=None, from_date=None, interval=None):
        self.strategy = strategy
        self.ticker = ticker
        self.tsym = tsym
        self.fsym = fsym
        self.to_date = to_date
        self.from_date = from_date
        self.interval = interval
        self.pnl = None
        self.cerebro = bt.Cerebro()

        if self.fsym != None:
            self.ticker = self.build_ticker()

    def build_ticker(self):
        return f'{self.tsym}{self.fsym}=X'

    def add_data(self):
        try:
            data = DownloadData(ticker=self.ticker, to_date=self.to_date, from_date=self.from_date, interval=self.interval).run()
            if data is not None:
                self.cerebro.adddata(data)
        except ValueError as e:
            print(f"Failed to add data: {e}")

    def add_strategy(self):
        self.cerebro.addstrategy(self.strategy)

    def add_analyzer(self):
        self.cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='evaluation')

    def add_commision(self):
        self.cerebro.broker.setcommission(commission=0.00002) 

    def run_backtrader(self):
        try:
            return self.cerebro.run()
        except IndexError as e:
            print(f"IndexError encountered, No Data Found for {self.ticker}")
            return []

    def evaluate(self):
        thestrats = self.run_backtrader()
        if thestrats:
            thestrat = thestrats[0]
            print('Evaluation metric', thestrat.analyzers.evaluation.get_analysis())

    def run(self):
        start_portfolio_value = self.cerebro.broker.getvalue()

        self.add_data()
        self.add_strategy()
        self.add_analyzer()
        self.add_commision()

        self.evaluate()

        end_portfolio_value = self.cerebro.broker.getvalue()
        self.pnl = end_portfolio_value - start_portfolio_value
        print(f'Starting Portfolio Value: {start_portfolio_value:.2f}')
        print(f'Final Portfolio Value: {end_portfolio_value:.2f}')
        print(f'PnL: {self.pnl:.2f}')
        
        # self.cerebro.plot()

