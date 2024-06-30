# “just before posting order” validation to make sure price and qty is sane, 
# validation of market data, you can’t trust it. 
# I’d follow a fail fast policy, if anything doesn’t seem right then terminate.
import pandas as pd
from datetime import datetime, timedelta


class ValidateOrder:
    def __init__(self, price, expected_price, order, num_orders_queued):
        self.price = price
        self.expected_price = expected_price
        self.order = order
        self.num_orders_queued = num_orders_queued
        self.orderbook = self.load_orderbook()

    def load_orderbook(self):
        orderbook = pd.read_csv('live_data/orderbook.csv')
        return orderbook
    
    def check_order_number(self):
        df = self.orderbook
        latest_date = pd.to_datetime(df.iloc[0]['Date'])
        time_delta = latest_date - timedelta(seconds=10)
        mask = (df['date'] > time_delta) & (df['date'] <= time_delta)
        df = df.loc[mask]

        if len(df) > 5:
            return True
        else:
            return False

    def price_in_range(self):
        if self.price < self.expected_price * 0.9:
            return False
        elif self.price > self.expected_price * 1.1:
            return False
        else:
            return True
        
    def order_throttle(self):
    
        # 1. Check exisiting order list, does this order already exist?
        if self.order in self.orderbook:
            return False
        
        # 2. Check time stamps for many orders in a short period of time
        if self.check_order_number():
            return False

        # 3. Check number of orders lines up
        if self.num_orders_queued > 10:
            return False
        
        return True

    def run(self):
        result = False
        result = self.price_in_range()
        result = self.order_throttle()

        return result