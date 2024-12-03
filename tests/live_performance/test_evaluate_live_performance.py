import unittest
from evaluation.evaluate_live_performance import EvaluateLivePerformance

def assert_calculations(self,
                        evaluator,
                        assert_realized,
                        assert_unrealized,
                        assert_roi):
    
    realized_profit = evaluator.calculate_realized_profit()
    unrealized_profit = evaluator.calculate_unrealized_profit()
    roi = evaluator.calculate_roi()

    self.assertAlmostEqual(realized_profit, assert_realized, places=2)
    self.assertAlmostEqual(unrealized_profit, assert_unrealized, places=2)
    self.assertAlmostEqual(roi, assert_roi, places=2)

    # Print final results
    print(f"Test: {self._testMethodName}")
    print(f"Realized Profit: {realized_profit:.3f} USD")
    print(f"Unrealized Profit: {unrealized_profit:.3f} USD")
    print(f"ROI: {roi:.3f}%\n")

class TestEvaluateLivePerformance(unittest.TestCase):
    def test_single_buy(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/single_buy.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, 0, 9999.8, 99.998)

    def test_single_sell(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/single_sell.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, 0, -10000.2, -100.002)

    def test_single_buy_sell(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/single_buy_sell.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, -0.2, 0, -0.002)

    def test_multiple_buy(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/multiple_buy.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, 0, 49999.0, 99.998)

    def test_multiple_sell(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/multiple_sell.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, 0, -50001.0, -100.002)

    def test_buy_buy_sell(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/buy_buy_sell.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, -0.2, 9999.399, 99.99)

    def test_sell_sell_buy(self):
        current_price = 2
        evaluator = EvaluateLivePerformance(current_price, "tests/live_performance/data/sell_sell_buy.csv")
        evaluator.load_data()
        assert_calculations(self, evaluator, -0.2, -10000.60, -100.008)