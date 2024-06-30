# “just before posting order” validation to make sure price and qty is sane, 
# validation of market data, you can’t trust it. 
# I’d follow a fail fast policy, if anything doesn’t seem right then terminate.

class ValidateOrder:
    def __init__(self, price, expected_price):
        self.price = price
        self.expected_price = expected_price

    def price_in_range(self):
        
        if self.price < self.expected_price * 0.9:
            return False
        elif self.price > self.expected_price * 1.1:
            return False
        else:
            return True
        
    def order_throttle(self):
        # 1. Check exisiting order list, does this order already exist?
        # 2. Check time stamps for many orders in a short period of time
        # 3. Check number of orders lines up

    def run(self):
        result = False
        result = self.price_in_range()
        result = self.order_throttle()

        return result