import backtrader as bt

def logdata(self):
    txt = []
    txt.append('{}'.format(len(self)))
    txt.append('{}'.format(self.data.datetime.datetime(0).isoformat()))
    txt.append('{:.2f}'.format(self.data.open[0]))
    txt.append('{:.2f}'.format(self.data.high[0]))
    txt.append('{:.2f}'.format(self.data.low[0]))
    txt.append('{:.2f}'.format(self.data.close[0]))
    txt.append('{:.2f}'.format(self.data.volume[0]))
    print(','.join(txt))

class TestStrategy(bt.Strategy):

    def __init__(self):
        print('TestStrategy')
        self.data_live = False

    def next(self):
        #logdata(self)
        if not self.data_live:
            return


class SimpleMovingAverageStrategy(bt.Strategy):
    params = (
        ('sma_period_fast', 10),   # Period for the fast moving average
        ('sma_period_slow', 30)    # Period for the slow moving average
    )

    def __init__(self):
        print('SimpleMovingAverageStrategy')
        self.sma_fast = bt.indicators.SimpleMovingAverage(self.data, period=self.params.sma_period_fast)
        self.sma_slow = bt.indicators.SimpleMovingAverage(self.data, period=self.params.sma_period_slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if self.crossover > 0:  # If fast SMA crosses above slow SMA
            self.buy()          # Enter long position
            self.signal = 'buy'
        elif self.crossover < 0:  # If fast SMA crosses below slow SMA
            self.sell()
            self.signal = 'sell'
        else:
            self.signal = 'hold'

        #logdata(self)

class MAcrossover(bt.Strategy): 
    # Moving average parameters
    params = (('pfast',30),('pslow',50),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def __init__(self):
        print('MAcrossover')
        self.dataclose = self.datas[0].close
        
		# Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pfast)
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            # if order.isbuy():
            #     self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            # elif order.issell():
            #     self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        # Check for open orders
        #logdata(self)
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades
                
            #If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                # self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
            #Otherwise if the 20 SMA is below the 50 SMA   
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                # self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.bar_executed + 5):
                # self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()

class RSI2Strategy(bt.Strategy):
    params = (
        ('rsi_period', 2),      # Period for the RSI calculation
        ('oversold_level', 10), # Threshold for oversold condition
        ('overbought_level', 90) # Threshold for overbought condition
    )

    def __init__(self):
        print('RSI2Strategy')
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)

    def next(self):
        #logdata(self)
        if self.rsi < self.params.oversold_level:
            self.buy()
        elif self.rsi > self.params.overbought_level:
            self.sell()


class BreakoutStrategy(bt.Strategy):
    params = (
        ('breakout_period', 20),  # Period for calculating breakout levels
        ('stop_loss', 0.02),       # Percentage for stop-loss order
        ('take_profit', 0.04)      # Percentage for take-profit order
    )

    def __init__(self):
        print('BreakoutStrategy')
        self.high = self.data.high
        self.low = self.data.low
        self.close = self.data.close

        self.breakout_level = bt.indicators.Highest(self.high(-1), period=self.params.breakout_period)
        self.stop_loss_price = self.close * (1 - self.params.stop_loss)
        self.take_profit_price = self.close * (1 + self.params.take_profit)

    def next(self):
        #logdata(self)
        if self.close > self.breakout_level:
            # Enter long position if price breaks above breakout level
            self.buy()

            # Place stop-loss order
            self.sell(exectype=bt.Order.Stop, price=self.stop_loss_price)

            # Place take-profit order
            self.sell(exectype=bt.Order.Limit, price=self.take_profit_price)

class BreakdownStrategy(bt.Strategy):
    params = (
        ('breakdown_period', 20),  # Period for calculating breakdown levels
        ('stop_loss', 0.02),        # Percentage for stop-loss order
        ('take_profit', 0.04)       # Percentage for take-profit order
    )

    def __init__(self):
        print('BreakdownStrategy')
        self.breakdown_level = bt.indicators.Lowest(self.data.low(-1), period=self.params.breakdown_period)
        self.stop_loss_price = self.data.close * (1 + self.params.stop_loss)
        self.take_profit_price = self.data.close * (1 - self.params.take_profit)

    def next(self):
        #logdata(self)
        if self.data.close < self.breakdown_level:
            # Enter short position if price breaks below breakdown level
            self.sell()

            # Place stop-loss order
            self.buy(exectype=bt.Order.Stop, price=self.stop_loss_price)

            # Place take-profit order
            self.buy(exectype=bt.Order.Limit, price=self.take_profit_price)

class RSIOverboughtOversoldStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def __init__(self):
        print('RSIOverboughtOversoldStrategy')
        self.rsi = bt.indicators.RSI_SMA(period=self.params.rsi_period)
        print("RSI Indicator initialized.")

    def next(self):
        print(f"Next called at {self.datas[0].datetime.datetime(0)}, Close: {self.data.close[0]}")
        if self.rsi < self.params.rsi_oversold:
            print(f"RSI below {self.params.rsi_oversold}: Buy signal generated.")
            self.buy()
        elif self.rsi > self.params.rsi_overbought:
            print(f"RSI above {self.params.rsi_overbought}: Sell signal generated.")
            self.sell()
