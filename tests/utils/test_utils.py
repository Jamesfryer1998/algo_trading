import unittest
from utils.json_tools import *
from utils.html_filler import *

class TestJsonTools(unittest.TestCase):
    def test_load_json(self):
        data = load_json("tests/utils/data/test_json.json")

        self.assertEqual(data["commission"], 1)

    def test_load_json(self):
        data = load_csv("tests/utils/data/test_csv.csv")
        self.assertEqual(data.iloc[0]["Ticker"], "GBPUSD")
        self.assertEqual(data.iloc[0]["Price"], 1)
        self.assertEqual(data.iloc[0]["Amount"], 10000.0)
        self.assertEqual(data.iloc[0]["Strategy"], "RSI")
        self.assertEqual(data.iloc[0]["Status"], "Filled")