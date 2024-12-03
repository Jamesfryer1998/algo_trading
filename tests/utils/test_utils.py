import unittest
from utils.json_tools import *
from utils.html_filler import *

class TestJsonTools(unittest.TestCase):
    def test_load_json(self):
        data = load_json("tests/utils/data/test_json.json")

        self.assertEqual(data["commission"], 1)